import hashlib
import logging

import backoff
import google.auth
import googleapiclient.errors
from googleapiclient import discovery


class Gcp:
    def __init__(
        self,
        gcp_project,
        target_lb,
        tcp_ssl_proxy=False,
        logger=None,
        http=None,
        metrics=None,
    ):
        """Create the GCP class"""

        self.gcp_project = gcp_project
        self.target_lb = target_lb
        self.tcp_ssl_proxy = tcp_ssl_proxy
        self.logger = logger if logger else logging.getLogger(__name__)
        self.metrics = metrics

        # Disable cache_discovery to prevent file_cache is unavailable when
        # using oauth2client >= 4.0.0 or google-auth error.
        # https://github.com/googleapis/google-api-python-client/issues/299#issuecomment-268915510
        args = {"cache_discovery": False}

        # http allows setting a custom http client, for example for testing.
        # The arguments http and credentials are mutually exclusive.
        if http:
            args["http"] = http
        else:  # pragma: no coverage
            # Ignore this statement in the coverage tests, as the tests would
            # be fairly meaningless.
            args["credentials"], _ = google.auth.default()

        # Create the google client with the key word arguments from above
        self.client = discovery.build("compute", "v1", **args)
        self.lb_client = (
            self.client.targetSslProxies()
            if tcp_ssl_proxy
            else self.client.targetHttpsProxies()
        )

    def send_metrics(self, *args, **kwargs):
        if self.metrics:
            self.metrics.send(*args, **kwargs)

    @staticmethod
    def create_cert_name(name):
        """Returns a Google approved name for the certificate"""
        # replace . with - in the certificate name
        # TODO: Match against  the regex provided by Google: '[a-z](?:[-a-z0-9]{0,61}[a-z0-9])?|[1-9][0-9]{0,19}'
        name = name.replace(".", "-").lower()

        # if longer then 62 characters, remove the last 8 characters and
        # append "-<HASH>" where HASH is the 7 first characters of the Sha256
        # hash of the name
        max_length = 62
        if len(name) > max_length:
            name = f"{name[:max_length-8]}-{hashlib.sha256(name.encode('UTF-8')).hexdigest()[:7]}"

        return name

    def get_target_kwargs(self):
        """Return LB type specific kwargs used to call methods on the
        load balancer client.

        Helper function because arguments differ between the
        targetSslProxy and targetHttpsProxy clients."""
        arg = "targetSslProxy" if self.tcp_ssl_proxy else "targetHttpsProxy"
        return {
            "project": self.gcp_project,
            arg: self.target_lb,
        }

    def create_gcp_certificate(self, name, cert, private_key, cert_chain):
        name = self.create_cert_name(name)

        # Check if the certificate exists and the return the certificate link
        # if it does.
        try:
            request = self.client.sslCertificates().get(
                project=self.gcp_project, sslCertificate=name
            )
            response = request.execute()

            # TODO: Make sure we're actually looking at the same certificate
            self.logger.info("Certificate existed, returning")
            return response["selfLink"]

        except googleapiclient.errors.HttpError as e:
            if e.resp.status != 404:
                raise e

        cert_bundle = cert
        if cert_chain:
            cert_bundle += f"\n{cert_chain}"

        ssl_certificate_body = {
            "name": name,
            "description": "Managed by Lemur",
            "certificate": cert_bundle,
            "privateKey": private_key,
        }

        request = self.client.sslCertificates().insert(
            project=self.gcp_project, body=ssl_certificate_body
        )
        response = request.execute()

        return response["targetLink"]

    def get_load_balancer(self):
        # returns a load balancer from gcp
        request = self.lb_client.get(**self.get_target_kwargs())
        response = request.execute()
        return response

    @backoff.on_exception(backoff.expo, googleapiclient.errors.HttpError, max_time=30)
    def update_load_balancer_ssl_certificates(self, certificate_list):
        # must check that number of certificates are <= 15, if not throw something
        request_body = {"sslCertificates": certificate_list}

        if len(request_body["sslCertificates"]) >= 15:
            raise ValueError(
                f"Too many certificates: {len(request_body['sslCertificates'])}. Max number is 15"
            )

        self.logger.debug(f"Updating GFE {self.target_lb}")
        request = self.lb_client.setSslCertificates(
            **self.get_target_kwargs(), body=request_body
        )
        return request.execute()

    def add_certificate(self, name, cert, private_key, cert_chain):
        # Limitations:
        # - Number of certificates in a load balancer is limited to 16
        # - Domain names per certificate is 100
        # - We should never delete certificate
        # - You need to upload your certificate first before you can add it to a load balancer
        # - You can only update certificates by getting the current list of certificates and appending
        try:
            self.logger.info(f"Creating GCP certficate resource {name}")
            cert_name = self.create_gcp_certificate(name, cert, private_key, cert_chain)

            self.send_metrics(
                "gcp_create_certificate",
                "counter",
                1,
                metric_tags={
                    "name": name,
                    "project": self.gcp_project,
                    "status": "success",
                },
            )

        except Exception as e:
            self.logger.error(
                "Failed to create GCP certificate resource.",
                extra={"certificate_name": name},
                exc_info=e,
            )
            self.send_metrics(
                "gcp_create_certificate",
                "counter",
                1,
                metric_tags={
                    "name": name,
                    "project": self.gcp_project,
                    "status": "failure",
                },
            )
            return

        try:
            self.logger.debug("Retrieving load balancer certificate list.")
            lb = self.get_load_balancer()
            ssl_certificates = lb.get("sslCertificates", [])
            self.logger.debug(
                "Successfully retrieved load balancer certificate list.",
                extra={"ssl_certificates": ssl_certificates},
            )
        except Exception as e:
            self.logger.error(
                "Failed to get certificate list from load balancer.", exc_info=e
            )
            return

        if cert_name not in ssl_certificates:
            # insert the certificate into the list of ssl_certificates
            new_certificate_list = [cert_name] + ssl_certificates

            self.logger.info(f"Attaching cert {name} to {self.target_lb}")
            try:
                self.update_load_balancer_ssl_certificates(new_certificate_list)
                self.send_metrics(
                    "gcp_attach_certificate",
                    "counter",
                    1,
                    metric_tags={
                        "name": name,
                        "project": self.gcp_project,
                        "target_load_balancer": self.target_lb,
                        "new_number_of_certificates": len(new_certificate_list),
                        "status": "success",
                    },
                )
            except Exception as e:
                self.logger.error(
                    "Failed to attach certificate to load balancer.",
                    extra={"new_certificate_list": new_certificate_list},
                    exc_info=e,
                )
                self.send_metrics(
                    "gcp_attach_certificate",
                    "counter",
                    1,
                    metric_tags={
                        "name": name,
                        "project": self.gcp_project,
                        "target_load_balancer": self.target_lb,
                        "status": "failure",
                    },
                )
                return
        else:
            self.logger.info(
                f"Target GFE {self.target_lb} already has cert {cert_name} attached, skipping."
            )

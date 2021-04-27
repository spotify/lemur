import logging
import time

from cryptography import x509
from cryptography.hazmat.backends import default_backend

import backoff
import google.auth
import googleapiclient.errors

from googleapiclient import discovery


class Gcp:
    def __init__(
        self,
        project,
        logger=None,
        http=None,
        metrics=None,
    ):
        """Initialize GCP client."""
        self.project = project
        self.logger = logger if logger else logging.getLogger(__name__)

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

    def _send_metrics(self, *args, **kwargs):
        if self.metrics:
            self.metrics.send(*args, **kwargs)

    def get_ssl_certificate_by_name(self, certificate_name):
        """Fetches and returns a SSL certificate resource from GCP."""
        return (
            self.client.sslCertificates()
            .get(project=self.project, sslCertificate=certificate_name)
            .execute()
        )

    def get_ssl_certificates(self):
        """Returns a list of all SSL certificates in the project."""
        certificates = []
        request = self.client.sslCertificates().list(project=self.project)
        while request is not None:
            response = request.execute()
            certificates.extend(response.get("items", []))
            request = self.client.sslCertificates().list_next(
                previous_request=request, previous_response=response
            )
        return certificates

    def _wait_for_operation(self, operation, max_time=10.0):
        """Wait until operation is successful by polling. If the operation fails this method
        throws an exception."""
        start = time.time()
        res = {}
        while True:
            if time.time() - start >= max_time:
                raise Exception(
                    f"Operation didn't finish within max_time ({max_time}s)."
                )

            res = (
                self.client.globalOperations()
                .get(project=self.project, operation=operation)
                .execute()
            )
            if res["status"] == "DONE":
                break

            time.sleep(1)

        if "error" in res:
            # grab the first error, which hopefully should always exist
            raise Exception(res["error"]["errors"][0]["message"])

    def upload_ssl_certificate(self, certificate_name, cert, private_key, cert_chain):
        """Upload a certificate to GCP. If the certificate is already uploaded under
        the same name this function returns the resource URI for the existing certificate."""
        cert_bundle = cert
        if cert_chain:
            cert_bundle += f"\n{cert_chain}"

        parsed_certificate = x509.load_pem_x509_certificate(
            cert_bundle.encode("utf-8"), default_backend()
        )

        # Check if the certificate exists and the return the certificate link
        # if it does.
        try:
            response = self.get_ssl_certificate_by_name(certificate_name)

            upstream_certificate = x509.load_pem_x509_certificate(
                response["certificate"].encode("utf-8")
            )

            if parsed_certificate != upstream_certificate:
                raise RuntimeError(
                    "A different certificate with the same name already exists"
                )

            self.logger.info("Certificate existed, returning")
            return response["selfLink"]
        except googleapiclient.errors.HttpError as e:
            if e.resp.status != 404:
                raise e

        ssl_certificate_body = {
            "name": certificate_name,
            "description": "Managed by Lemur",
            "certificate": cert_bundle,
            "privateKey": private_key,
        }

        request = self.client.sslCertificates().insert(
            project=self.project, body=ssl_certificate_body
        )

        # response is an operation, wait for it to finish
        response = request.execute()
        self._wait_for_operation(response["name"])

        return response["targetLink"]

    def get_load_balancers(self):
        """Fetches and returns all HTTPS and SSL load balancers from GCP."""
        lbs = []

        # Fetch HTTPS load balancers
        request = self.client.targetHttpsProxies().list(project=self.project)
        while request is not None:
            response = request.execute()
            lbs.extend(response.get("items", []))

            request = self.client.targetHttpsProxies().list_next(
                previous_request=request, previous_response=response
            )

        # Fetch TCP SSL load balancers
        request = self.client.targetSslProxies().list(project=self.project)
        while request is not None:
            response = request.execute()
            lbs.extend(response.get("items", []))

            request = self.client.targetSslProxies().list_next(
                previous_request=request, previous_response=response
            )

        return lbs

    def get_load_balancer_by_name_and_kind(self, name, kind):
        """Fetches and returns a load balancer resource from GCP.

        Args:
            name (str): Name of the load balancer
            kind (str): Load balancer kind.
                Example: compute#targetHttpsProxy or compute#targetSslProxy
        """
        if kind == "compute#targetHttpsProxy":
            request = self.client.targetHttpsProxies().get(
                project=self.project, targetHttpsProxy=name
            )
        elif kind == "compute#targetSslProxy":
            request = self.client.targetSslProxies().get(
                project=self.project, targetSslProxy=name
            )
        else:
            raise Exception("Invalid load balancer kind.")

        return request.execute()

    @backoff.on_exception(backoff.expo, googleapiclient.errors.HttpError, max_time=30)
    def set_load_balancer_ssl_certificates(self, name, kind, certificate_list):
        """Fetches and returns a load balancer resource from GCP.

        Args:
            name (str): Name of the load balancer
            kind (str): Load balancer kind.
                Example: compute#targetHttpsProxy or compute#targetSslProxy
            certificate_list (List[str]): List of certificates resource URIs.
        """
        # must check that number of certificates are <= 15
        if len(certificate_list) > 15:
            raise ValueError(
                f"Too many certificates: {len(certificate_list)}. Max number is 15"
            )

        self.logger.debug(
            f"Setting ssl certificate list for load balancer {name} to {certificate_list}."
        )
        request_body = {"sslCertificates": certificate_list}

        if kind == "compute#targetHttpsProxy":
            request = self.client.targetHttpsProxies().setSslCertificates(
                project=self.project,
                targetHttpsProxy=name,
                body=request_body,
            )
        elif kind == "compute#targetSslProxy":
            request = self.client.targetSslProxies().setSslCertificates(
                project=self.project,
                targetSslProxy=name,
                body=request_body,
            )
        else:
            raise Exception("Invalid load balancer kind.")

        return request.execute()

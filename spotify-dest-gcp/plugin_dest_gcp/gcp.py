from googleapiclient import discovery
import googleapiclient.errors
import google.auth
import backoff
import hashlib
import logging
import pathlib
import re


class Gcp:
    def __init__(self, gcp_project, target_lb, logger=None, http=None):
        """Create the GCP class"""

        self.gcp_project = gcp_project
        self.target_lb = target_lb
        self.logger = logger if logger else logging.getLogger(__name__)

        # Disable cache_discovery to prevent file_cache is unavailable when
        # using oauth2client >= 4.0.0 or google-auth error.
        # https://github.com/googleapis/google-api-python-client/issues/299#issuecomment-268915510
        args = {"cache_discovery": False}

        # http allows setting a custom http client, for example for testing.
        # The arguments http and credentials are mutually exclusive.
        if http:
            args["http"] = http
        else:
            credentials, _ = google.auth.default()
            args["credentials"] = credentials

        # Create the google client with the key word arguments from above
        self.client = discovery.build("compute", "v1", **args)

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

    def create_gcp_certificate(self, name, cert, private_key, cert_chain):
        name = create_cert_name(name)

        # make sure certificate doesn't exist in the GCP project
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
            self.logger.info("Certificate does not exist, uploading")

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
        request = self.client.targetHttpsProxies().get(
            project=self.gcp_project, targetHttpsProxy=self.target_lb
        )
        response = request.execute()
        return response

    @backoff.on_exception(backoff.expo, googleapiclient.errors.HttpError, max_time=30)
    def update_load_balancer_ssl_certificates(self, certificate_list):
        # must check that number of certificates are <= 16, if not throw something
        request_body = {"sslCertificates": certificate_list}

        if len(request_body["sslCertificates"]) > 16:
            raise ValueError(
                f"Too many certificates {len(request_body['sslCertificates'])}. Max number is 16"
            )

        self.logger.debug(f"Updating GFE {self.target_lb}")
        request = self.client.targetHttpsProxies().setSslCertificates(
            project=self.gcp_project, targetHttpsProxy=self.target_lb, body=request_body
        )
        response = request.execute()

    def add_certificate(self, name, cert, private_key, cert_chain):
        # Limitations:
        # - Number of certificates in a load balancer is limited to 16
        # - Domain names per certificate is 100
        # - We should never delete certificate
        # - You need to upload your certificate first before you can add it to a load balancer
        # - You can only update certificates by getting the current list of certificates and appending
        cert_name = self.create_gcp_certificate(name, cert, private_key, cert_chain)

        lb = self.get_load_balancer()
        ssl_certificates = lb.get("sslCertificates", [])

        if cert_name not in ssl_certificates:
            # insert the certificate into the list of ssl_certificates
            new_certificate_list = [cert_name] + ssl_certificates

            # sanity check before setting ssl certificates
            if len(new_certificate_list) < len(ssl_certificates):
                raise RuntimeError("Error when creating the new certificate list")

            self.logger.info(f"Attaching cert {name} to {self.target_lb}")
            self.update_load_balancer_ssl_certificates(new_certificate_list)
        else:
            self.logger.info(
                f"Target GFE {self.target_lb} already has cert {cert_name} attached, skipping."
            )


if __name__ == "__main__":

    folder = pathlib.Path(__file__).resolve().parent
    with open(folder / "../tests/assets/cert.pem") as f:
        cert = f.read()

    with open(folder / "../tests/assets/key.pem") as f:
        key = f.read()

    logging.basicConfig(level=logging.DEBUG)
    gcp = Gcp("xpn-cert-management", "https-test-lb-target-proxy")
    gcp.add_certificate(
        "example.com-selfsigned-20201124-20211124-B4DA1AE31F71BDCB", cert, key, None
    )

import logging
import json

import google.api_core.exceptions
from google.cloud import secretmanager

from cryptography import x509
from cryptography.hazmat.backends import default_backend
from google.protobuf.timestamp_pb2 import Timestamp

from lemur.extensions import metrics  # pylint: disable=import-error
from lemur.plugins.base import Plugin
from lemur.plugins.bases import (
    DestinationPlugin,
)  # pylint: disable=import-error


class GcpSecretManager:
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

    def get_ssl_certificate_by_name(self, certificate_name):
        client = secretmanager.SecretManagerServiceClient()
        secrets = client.list_secrets(request={
            "parent": "projects/" + self.project
        })

        # secret.name e.g. projects/418358634264/secrets/spotify-com-20230406-3bcb8
        # certificate_name e.g. spotify-com-20230406-3bcb8
        # "projects/418358634264/secrets/spotify-com-20230406-3bcb8".split("/")[-1] == "spotify-com-20230406-3bcb8"
        secret_names = [s.name.split("/")[-1] for s in secrets]

        self.logger.debug("secret to check for: %s | secret names: %s", certificate_name, secret_names)

        if certificate_name in secret_names:
            self.logger.debug("found secret version with name %s", certificate_name)
            return True
        self.logger.debug("no secret with name %s", certificate_name)
        return False

    def upload_ssl_certificate(self, certificate_name, cert, private_key, cert_chain):
        """Upload a certificate to GCP Secret manager. If the certificate is already uploaded under
        the same name do nothing as spotify-lemur gives every cert a unique name, rather new versions
        of the same logical cert having the exact same name as the certs they replace."""
        cert_bundle = cert
        if cert_chain:
            cert_bundle += f"\n{cert_chain}"

        parsed_certificate = x509.load_pem_x509_certificate(
            cert_bundle.encode("utf-8"), default_backend()
        )

        ssl_certificate_body = {
            "name": certificate_name,
            "description": "Managed by Lemur",
            "certificate": cert_bundle,
            "privateKey": private_key,
        }

        secretClient = secretmanager.SecretManagerServiceClient()
        secret_name = "projects/" + self.project + "/secrets/" + certificate_name

        try:
            parent_secret = secretClient.get_secret(request={
                "name": secret_name
            })
            self.logger.info("Found previous version of secret %s, doing nothing", secret_name)
            return secret_name
        except google.api_core.exceptions.NotFound:
            # create new secret
            expire_time = Timestamp();
            expire_time.FromDatetime(parsed_certificate.not_valid_after)

            createSecretRequest = {
                "parent": "projects/" + self.project,
                "secret_id": certificate_name,
                "secret": {
                    "replication": {"automatic": {}},
                    "labels": [("lemur", "lemur-managed")],
                    "expire_time": expire_time,  # parsed_certificate.not_valid_after,
                },
            }

            self.logger.debug(createSecretRequest)
            parent_secret = secretClient.create_secret(createSecretRequest)

        version = secretClient.add_secret_version(request={
            "parent": parent_secret.name,
            "payload": {"data": json.dumps(ssl_certificate_body).encode('utf8')}
        })

        return secret_name


def gcp_secretmanager_client(options):
    return GcpSecretManager(Plugin.get_option("gcp-project", options), metrics=metrics)


class GcpSecretManagerDestination(DestinationPlugin):
    title = "GCP Secret Manager Destination"
    slug = "gcp_secretmanager_destination"
    description = "GCP Secret Manager Destination Plugin"

    author = "Your Name"
    author_url = "https://github.com/yourname/lemur_pluginname"

    options = [
        {
            "name": "gcp-project",
            "type": "str",
            "required": True,
        },
    ]
    additional_options = []

    def upload(
            self, name, body, private_key, cert_chain, options, **kwargs
    ):  # pylint: disable=unused-argument
        client = gcp_secretmanager_client(options)
        client.upload_ssl_certificate(name, body, private_key, cert_chain)

        metrics.send(
            "gcp_secretmanager_upload_certificate",
            "counter",
            1,
            metric_tags={
                "name": name,
                "dest_project": client.project,
                "status": "success",
            },
        )

    def verify(self, cert_name, options):
        """Verify that a certificate has been uploaded to GCP Secret Manager."""
        client = gcp_secretmanager_client(options)

        return client.get_ssl_certificate_by_name(cert_name)

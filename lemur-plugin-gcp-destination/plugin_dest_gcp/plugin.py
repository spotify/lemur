from lemur.extensions import metrics  # pylint: disable=import-error
from lemur.plugins.bases import DestinationPlugin  # pylint: disable=import-error

from .gcp import Gcp


class GcpDestination(DestinationPlugin):
    title = "Gcp Destination"
    slug = "gcp_destination"
    description = "Gcp Destination Plugin"

    author = "Your Name"
    author_url = "https://github.com/yourname/lemur_pluginname"

    options = [
        {
            "name": "gcp-project",
            "type": "str",
            "required": True,
        },
        {
            "name": "target-proxy-name",
            "type": "str",
            "required": True,
        },
        {
            "name": "tcp-ssl-proxy",
            "type": "bool",
            "required": False,
            "default": False,
        },
    ]
    additional_options = []

    def upload(
        self, name, body, private_key, cert_chain, options, **kwargs
    ):  # pylint: disable=unused-argument
        gcp = self.get_gcp(options)
        gcp.add_certificate(name, body, private_key, cert_chain)

    def get_gcp(self, options):
        gcp = Gcp(
            self.get_option("gcp-project", options),
            self.get_option("target-proxy-name", options),
            self.get_option("tcp-ssl-proxy", options),
            metrics=metrics,
        )
        return gcp

    def verify(self, cert_name, options):
        gcp = self.get_gcp(options)
        gcp_cert_name = Gcp.create_cert_name(cert_name)
        return gcp_cert_name in gcp.get_load_balancer().get("sslCertificates", [])

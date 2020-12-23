from flask import current_app  # pylint: disable=import-error
from lemur.plugins.bases import \
    DestinationPlugin  # pylint: disable=import-error

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
    ]
    additional_options = []

    def upload(
        self, name, body, private_key, cert_chain, options, **kwargs
    ):  # pylint: disable=unused-argument
        gcp = Gcp(
            self.get_option("gcp-project", options),
            self.get_option("target-proxy-name", options),
            logger=current_app.logger,
        )

        gcp.add_certificate(name, body, private_key, cert_chain)

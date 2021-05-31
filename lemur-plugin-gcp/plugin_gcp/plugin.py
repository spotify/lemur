import logging
import pem
from lemur.extensions import metrics  # pylint: disable=import-error
from lemur.plugins.base import Plugin
from lemur.plugins.bases import (
    DestinationPlugin,
    SourcePlugin,
)  # pylint: disable=import-error

import googleapiclient.errors

from .gcp import Gcp


logger = logging.getLogger(__name__)


def get_gcp_client_from_options(options):
    return Gcp(Plugin.get_option("gcp-project", options), metrics=metrics)


class GcpSource(SourcePlugin):
    title = "Gcp Source"
    slug = "gcp_source"
    description = "Gcp Source Plugin"

    author = "Your Name"
    author_url = "https://github.com/yourname/lemur_pluginname"

    options = [
        {
            "name": "gcp-project",
            "type": "str",
            "required": True,
        },
    ]

    def get_certificates(self, options, **kwargs):
        client = get_gcp_client_from_options(options)
        response = client.get_ssl_certificates()

        certs = []
        for item in response:
            if item["type"] == "MANAGED":
                # skip certificates managed by Google
                continue

            body, *chain = pem.parse(item["certificate"].encode("utf-8"))
            certs.append(
                dict(
                    body=body.as_text(),
                    chain="".join(map(lambda c: c.as_text(), chain)),
                    name=item["name"],
                )
            )

        return list(reversed(certs))

    def get_certificate_by_name(self, certificate_name, options, **kwargs):
        client = get_gcp_client_from_options(options)
        gcp_cert = client.get_ssl_certificate_by_name(certificate_name)
        body, *chain = pem.parse(gcp_cert["certificate"].encode("utf-8"))
        return dict(
            body=body.as_text(),
            chain="".join(map(lambda c: c.as_text(), chain)),
            name=gcp_cert["name"],
        )

    def get_endpoints(self, options, **kwargs):
        client = get_gcp_client_from_options(options)
        endpoints = []

        # build a map for ssl certificates to lookup self-link -> certificate name
        ssl_certificates = {}
        for item in client.get_ssl_certificates():
            ssl_certificates[item["selfLink"]] = item

        def load_balancer_to_endpoint(lb):
            """Create a list of endpoints.

            An endpoint in the case of GCP will be a load-balancer/certificate pair since
            Lemur doesn't really have support for multiple certs per endpoint."""
            endpoints = []
            for certificate in lb["sslCertificates"]:
                gcp_cert = ssl_certificates[certificate]

                # display name for this endpoint
                name = f"{client.project}/{lb['name']}/{gcp_cert['name']}"

                # we treat dnsname as an external id to match a Lemur endpoint to
                # a (gcp lb, certificate) pair.
                # dnsname is something from the AWS world where each LB get its own
                # unique dnsname.
                dnsname = f"{client.project}/{lb['name']}/{gcp_cert['id']}"

                endpoints.append(
                    dict(
                        name=name,
                        dnsname=dnsname,
                        port=0,
                        type=lb["kind"],
                        certificate_name=gcp_cert["name"],
                        policy=dict(name="N/A", ciphers=["N/A"]),
                    )
                )
            return endpoints

        for lb in client.get_load_balancers():
            endpoints.extend(load_balancer_to_endpoint(lb))

        return endpoints

    def update_endpoint(self, endpoint, cert_name):
        client = get_gcp_client_from_options(endpoint.source.options)

        # dnsname is <GCP_PROJECT>/<TARGET_PROXY_NAME>/<CERTIFICATE_ID>
        target_proxy_name = endpoint.dnsname.split("/", 2)[1]

        # check so the new certificate is uploaded and we can find it
        gcp_cert = client.get_ssl_certificate_by_name(cert_name)

        # prepend to list if it doesn't exist
        lb = client.get_load_balancer_by_name_and_kind(target_proxy_name, endpoint.type)

        if gcp_cert["selfLink"] in lb["sslCertificates"]:
            # cert is already attached
            logger.info(
                f"Certificate {cert_name} is already attached to {lb['name']}, skipping."
            )
            return

        new_certificate_list = [gcp_cert["selfLink"]] + lb["sslCertificates"]
        lb["sslCertificates"] = new_certificate_list
        client.set_load_balancer_ssl_certificates(target_proxy_name, endpoint.type, lb)

        logger.info(f"Attached certificate {cert_name} to {lb['name']}")

    def remove_certificate(self, endpoint, cert_name):
        client = get_gcp_client_from_options(endpoint.source.options)

        # dnsname is <GCP_PROJECT>/<TARGET_PROXY_NAME>/<CERTIFICATE_ID>
        target_proxy_name = endpoint.dnsname.split("/", 2)[1]

        # get certificate self link name
        gcp_cert = client.get_ssl_certificate_by_name(cert_name)

        # remove the cert from the list of ssl certificates and update the lb
        lb = client.get_load_balancer_by_name_and_kind(target_proxy_name, endpoint.type)

        if gcp_cert["selfLink"] not in lb["sslCertificates"]:
            # cert is already removed
            logger.info(
                f"Certificate {cert_name} is not attached to {lb['name']}, skipping."
            )
            return

        new_certificate_list = [
            c for c in lb["sslCertificates"] if c != gcp_cert["selfLink"]
        ]
        lb["sslCertificates"] = new_certificate_list

        client.set_load_balancer_ssl_certificates(target_proxy_name, endpoint.type, lb)

        logger.info(f"Removed certificate {cert_name} from {lb['name']}")


class GcpDestination(DestinationPlugin):
    title = "Gcp Destination"
    slug = "gcp_destination"
    description = "Gcp Destination Plugin"

    author = "Your Name"
    author_url = "https://github.com/yourname/lemur_pluginname"

    # not really necessary, but avoid having to add a source for the same
    # destination. this requires the celery task sync_source_destination to
    # run periodically (or when a destination is added?)
    # # sync_as_source = True
    # # sync_as_source_name = GcpSource.slug

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
        client = get_gcp_client_from_options(options)
        client.upload_ssl_certificate(name, body, private_key, cert_chain)

        metrics.send(
            "gcp_upload_certificate",
            "counter",
            1,
            metric_tags={
                "name": name,
                "project": client.project,
                "status": "success",
            },
        )

    def verify(self, cert_name, options):
        """Verify that a certificate has been uploaded to GCP."""
        client = get_gcp_client_from_options(options)

        try:
            client.get_ssl_certificate_by_name(cert_name)
            return True
        except googleapiclient.errors.HttpError as e:
            if e.resp.status != 404:
                raise e
        return False

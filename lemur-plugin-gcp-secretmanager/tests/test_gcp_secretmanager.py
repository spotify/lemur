import json
import pathlib

# import pytest

#import pathlib
#import plugin_gcp_secretmanager.plugin as p
#import json
#
#test_folder = pathlib.Path("tests").resolve().parent
#cert = (test_folder / "lemur-plugin-gcp-secretmanager/tests/assets/2022-cert.pem").read_text()
#private_key = (test_folder / "lemur-plugin-gcp-secretmanager/tests/assets/2022-key.pem").read_text()
#client = p.GcpSecretManager("atc-rnd")
#client.upload_ssl_certificate("mat5", cert, private_key, None)


def test_create_certificate(gcp_secretmanager_client):
    """Test that the client can create a new certificate

    Mocks the requests to Google with a preset response and compare the result.

    """
    test_folder = pathlib.Path(__file__).resolve().parent

    # Load the required test data
    cert = (test_folder / "assets/cert.pem").read_text()
    private_key = (test_folder / "assets/key.pem").read_text()
    cert_chain = None

    # Load the mocked GCP data
    create_cert_response = (
        test_folder / "assets/create_cert_response.json"
    ).read_text()

    operation_response = (test_folder / "assets/operation_response.json").read_text()

    # Create the client
    client = gcp_secretmanager_client(
        responses=[
            ({"status": "404"}, "certificate does not exist"),
            ({"status": "200"}, create_cert_response),
            ({"status": "200"}, operation_response),
        ],
    )

    cert_link = client.upload_ssl_certificate(
        "a-new-test-certificate", cert, private_key, cert_chain
    )

    assert (
        cert_link
        == "https://www.googleapis.com/compute/v1/projects/xpn-cert-management/global/sslCertificates/a-new-test-certificate"
    )

import pytest
import googleapiclient.http
import pathlib

import plugin_dest_gcp.gcp


@pytest.fixture
def get_gcp_client():
    def inner(
        gcp_project="xpn-cert-management",
        target_lb="https-python-test-lb",
        tcp_ssl_proxy=False,
        responses=None,
    ):
        # HttpMock/HttpMockSequence allows us to set custom responses
        # to the API calls the client makes.
        # https://github.com/googleapis/google-api-python-client/blob/master/docs/mocks.md

        if responses is None:
            responses = []

        # Add a mocked response from the compute engine
        # Loads mock response from
        # https://www.googleapis.com/discovery/v1/apis/compute/v1/rest
        test_folder = pathlib.Path(__file__).resolve().parent
        compute_discovery = (
            test_folder / "assets/compute_discovery_response.json"
        ).read_text()

        responses.insert(0, ({"status": "200"}, compute_discovery))

        http = googleapiclient.http.HttpMockSequence(responses)

        return plugin_dest_gcp.gcp.Gcp(
            gcp_project=gcp_project,
            target_lb=target_lb,
            tcp_ssl_proxy=tcp_ssl_proxy,
            http=http,
        )

    return inner


@pytest.fixture
def test_certificate():
    """Give a test certificate, as (name, cert, key)"""

    name = "example.com-selfsigned-20201124-20211124-B4DA1AE31F71BDCB"

    test_folder = pathlib.Path(__file__).resolve().parent

    with open(test_folder / "assets/cert.pem") as f:
        cert = f.read()

    with open(test_folder / "assets/key.pem") as f:
        key = f.read()

    return name, cert, key

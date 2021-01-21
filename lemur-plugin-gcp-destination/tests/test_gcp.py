import json
import pathlib

import pytest


@pytest.mark.parametrize("tcp_ssl_proxy", [True, False])
def test_get_load_balancers(get_gcp_client, tcp_ssl_proxy):
    """Test that the client can get a load balancer.

    Mocks the requests to Google with a preset response and compare the result
    from get_load_balancer with this response.

    Google mock expects a JSON string, but for comparison the dictionary is used.
    """
    # Load the pre-defined load balancer respones.
    test_folder = pathlib.Path(__file__).resolve().parent

    # Load the mock data as strings
    load_balancer_response = (
        test_folder / "assets/load_balancer_response.json"
    ).read_text()
    http_proxy_response = (
        test_folder / "assets/target_http_proxy_response.json"
    ).read_text()

    client = get_gcp_client(
        gcp_project="xpn-cert-management",
        target_lb="https-python-test-lb",
        responses=[
            ({"status": "200"}, load_balancer_response),
            ({"status": "200"}, http_proxy_response),
        ],
    )

    client_response = client.get_load_balancer()

    assert client_response == json.loads(load_balancer_response)


@pytest.mark.parametrize("tcp_ssl_proxy", [True, False])
def test_create_cert_when_exists(get_gcp_client, tcp_ssl_proxy):
    """Test that the client can return the path to an existing cert

    Mocks the requests to Google with a preset response and compare the result.
    """
    test_folder = pathlib.Path(__file__).resolve().parent

    # Load the required test data
    cert = (test_folder / "assets/cert.pem").read_text()
    private_key = (test_folder / "assets/key.pem").read_text()
    cert_chain = None

    # Load the mock data as strings
    cert_response = (test_folder / "assets/cert_response.json").read_text()

    # Create the client
    client = get_gcp_client(
        gcp_project="xpn-cert-management",
        target_lb="https-python-test-lb",
        tcp_ssl_proxy=tcp_ssl_proxy,
        responses=[({"status": "200"}, cert_response)],
    )

    cert_link = client.create_gcp_certificate(
        "a-test-certificate", cert, private_key, cert_chain
    )

    assert (
        cert_link
        == "https://www.googleapis.com/compute/v1/projects/xpn-cert-management/global/sslCertificates/a-test-certificate"
    )


@pytest.mark.parametrize("tcp_ssl_proxy", [True, False])
def test_create_certificate(get_gcp_client, tcp_ssl_proxy):
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

    # Create the client
    client = get_gcp_client(
        gcp_project="xpn-cert-management",
        target_lb="https-pthon-test-lb",
        responses=[
            ({"status": "404"}, "certificate does not exist"),
            ({"status": "200"}, create_cert_response),
        ],
    )

    cert_link = client.create_gcp_certificate(
        "a-new-test-certificate", cert, private_key, cert_chain
    )

    assert (
        cert_link
        == "https://www.googleapis.com/compute/v1/projects/xpn-cert-management/global/sslCertificates/a-new-test-certificate"
    )


@pytest.mark.parametrize("tcp_ssl_proxy", [True, False])
def test_update_lb_ssl_cert(get_gcp_client, tcp_ssl_proxy):
    """Test that the load balancer can be updated with a new certificate.

    This is not a great test as we do not handle the response. This test does
    not really test anything.
    """

    # Create the client
    client = get_gcp_client(
        gcp_project="xpn-cert-management",
        target_lb="https-test-lb-target-proxy",
        tcp_ssl_proxy=tcp_ssl_proxy,
        responses=[
            (
                {"status": "200"},
                '{ "message": "success" }',
            ),
        ],
    )

    assert (
        client.update_load_balancer_ssl_certificates(["cert-a", "cert-b"])["message"]
        == "success"
    )


@pytest.mark.parametrize("tcp_ssl_proxy", [True, False])
def test_update_lb_error(get_gcp_client, tcp_ssl_proxy):
    """Test that the load balancer update raises ValueError with to many certs.

    Mocks the request to GCP with preset responses.
    """

    # Create the client
    client = get_gcp_client(
        gcp_project="xpn-cert-management",
        target_lb="https-test-lb-target-proxy",
        tcp_ssl_proxy=tcp_ssl_proxy,
    )

    with pytest.raises(ValueError):
        client.update_load_balancer_ssl_certificates(["cert-a"] * 20)

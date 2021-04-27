import json
import pathlib

import pytest


def test_upload_cert_when_exists(get_gcp_client):
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
        responses=[({"status": "200"}, cert_response)],
    )

    cert_link = client.upload_ssl_certificate(
        "a-test-certificate", cert, private_key, cert_chain
    )

    assert (
        cert_link
        == "https://www.googleapis.com/compute/v1/projects/xpn-cert-management/global/sslCertificates/a-test-certificate"
    )


def test_upload_cert_with_same_name(get_gcp_client):
    """Test that the client should fail if we try to upload a different certificate
    with the same name.

    Mocks the requests to Google with a preset response and compare the result.
    """
    test_folder = pathlib.Path(__file__).resolve().parent

    # Load the required test data
    cert = (test_folder / "assets/cert2.pem").read_text()
    private_key = (test_folder / "assets/key.pem").read_text()
    cert_chain = None

    # Load the mock data as strings
    cert_response = (test_folder / "assets/cert_response.json").read_text()

    # Create the client
    client = get_gcp_client(
        responses=[({"status": "200"}, cert_response)],
    )

    with pytest.raises(RuntimeError) as excinfo:
        client.upload_ssl_certificate(
            "a-test-certificate", cert, private_key, cert_chain
        )

    assert "A different certificate with the same name already exists" == str(
        excinfo.value
    )


def test_create_certificate(get_gcp_client):
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
    client = get_gcp_client(
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


def test_get_ssl_certificates(get_gcp_client):
    """Test that we can fetch SSL certificates from a GCP project."""
    test_folder = pathlib.Path(__file__).resolve().parent

    # Load the mocked GCP data
    list_ssl_certificates_response = (
        test_folder / "assets/list_ssl_certificates_response.json"
    ).read_text()

    client = get_gcp_client(
        responses=[
            ({"status": "200"}, list_ssl_certificates_response),
        ],
    )

    certs = client.get_ssl_certificates()
    assert len(certs) == 1


def test_get_load_balancers(get_gcp_client):
    """Test that the client can get HTTPS and TCP SSL load balancers."""
    # Load the pre-defined load balancer respones.
    test_folder = pathlib.Path(__file__).resolve().parent

    # Load the mock data as strings
    list_target_https_proxies_response = (
        test_folder / "assets/list_target_https_proxies_response.json"
    ).read_text()

    list_target_ssl_proxies_response = (
        test_folder / "assets/list_target_ssl_proxies_response.json"
    ).read_text()

    client = get_gcp_client(
        responses=[
            ({"status": "200"}, list_target_https_proxies_response),
            ({"status": "200"}, list_target_ssl_proxies_response),
        ],
    )

    lbs = client.get_load_balancers()
    assert len(lbs) == 2


@pytest.mark.parametrize("kind", ["compute#targetHttpsProxy", "compute#targetSslProxy"])
def test_get_load_balancer_by_name_and_kind(get_gcp_client, kind):
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

    client = get_gcp_client(
        responses=[
            ({"status": "200"}, load_balancer_response),
        ],
    )

    client_response = client.get_load_balancer_by_name_and_kind(
        "https-python-test-lb", kind
    )

    assert client_response == json.loads(load_balancer_response)


@pytest.mark.parametrize("kind", ["compute#targetHttpsProxy", "compute#targetSslProxy"])
def test_set_load_balancer_ssl_certificates(get_gcp_client, kind):
    """Test that the load balancer can be updated with a new certificate."""

    # Create the client
    client = get_gcp_client(
        responses=[
            (
                {"status": "200"},
                '{ "message": "success" }',
            ),
        ],
    )

    response = client.set_load_balancer_ssl_certificates(
        "test-lb", kind, ["cert-a", "cert-b"]
    )

    assert response["message"] == "success"


@pytest.mark.parametrize("kind", ["compute#targetHttpsProxy", "compute#targetSslProxy"])
def test_update_lb_error(get_gcp_client, kind):
    """Test that the load balancer update raises ValueError with too many certs (> 15)."""

    # Create the client
    client = get_gcp_client()

    with pytest.raises(ValueError):
        client.set_load_balancer_ssl_certificates("test-lb", kind, ["cert-a"] * 20)

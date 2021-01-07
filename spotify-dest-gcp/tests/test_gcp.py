import json
import pathlib


def test_get_load_balancers(get_gcp_client):
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


def test_create_cert_when_exists(get_gcp_client):
    """Test that the client can return the path to an existing cert

    Mocks the requests to Google with a preset response and compare the result.
    """
    # Load the pre-defined cert
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
        responses=[({"status": "200"}, cert_response)],
    )

    cert_link = client.create_gcp_certificate(
        "a-test-certificate", cert, private_key, cert_chain
    )

    assert (
        cert_link
        == "https://www.googleapis.com/compute/v1/projects/xpn-cert-management/global/sslCertificates/a-test-certificate"
    )


def test_create_certificate(get_gcp_client):
    """Test that the client can create a new certificate

    Mocks the requests to Google with a preset response and compare the result.
    """
    # Load the pre-defined cert
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
        target_lb="https-test-lb-target-proxy",
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

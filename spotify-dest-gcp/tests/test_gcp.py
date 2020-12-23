import pathlib
import json


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

def test_get_certificate_name(get_gcp_client):
    """Test that a valid certificate name is returned."""
    client = get_gcp_client()

    invalid_cert_name = "my.certificate"
    valid_cert_name = "my-certificate"

    assert client.create_cert_name(invalid_cert_name) == valid_cert_name


def test_get_certificate_name_hashed(get_gcp_client):
    """Test that too long certificate names are truncated"""
    client = get_gcp_client()

    too_long_name = 80 * "abcd"

    assert len(client.create_cert_name(too_long_name)) == 62

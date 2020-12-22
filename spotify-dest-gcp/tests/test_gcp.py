import pytest

import googleapiclient.http

from .context import plugin_dest_gcp


@pytest.fixture
def get_gcp_client():
    # HttpMock/HttpMockSequence allows us to set custom responses
    # to the API calls the client makes.
    # https://github.com/googleapis/google-api-python-client/blob/master/docs/mocks.md
    def inner(responses=None):
        http = googleapiclient.http.HttpMockSequence(
            [
                # TODO: add discovery mock https://www.googleapis.com/discovery/v1/apis/compute/v1/rest
            ]
            + []
            if responses is None
            else responses
        )

        return plugin_dest_gcp.gcp.Gcp(http=http)

    return inner


def test_some_method(get_gcp_client):
    client = get_gcp_client(
        [
            # (headers, body),
        ]
    )
    assert client.add_certificate() == True

import pathlib

from setuptools import setup, find_packages

current = pathlib.Path(__file__).resolve().parent

setup(
    name="spotify_gcp",
    entry_points={
        "lemur.plugins": [
            "gcp_source = plugin_gcp.plugin:GcpSource",
            "gcp_dest = plugin_gcp.plugin:GcpDestination",
        ],
    },
    install_requires=[
        "google-api-python-client == 1.12.8",
        "google-oauth == 1.0.1",
        "backoff == 1.10",
        "google_api_core == 2.2.2",
    ],
    packages=find_packages(),
    test_requires=(current / "requirements-test.txt").read_text().splitlines(),
)

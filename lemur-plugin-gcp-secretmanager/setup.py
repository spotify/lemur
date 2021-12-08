import pathlib

from setuptools import setup, find_packages

current = pathlib.Path(__file__).resolve().parent

setup(
    name="spotify_gcp_secretmanager",
    entry_points={
        "lemur.plugins": [
            # "gcp_source = plugin_gcp.plugin:GcpSource",
            "gcp_secretmanager_dest = plugin_gcp_secretmanager.plugin:GcpSecretManagerDestination",
        ],
    },
    install_requires=[
        # "google-api-python-client == 1.12.8",
        # "google-oauth == 1.0.1",
        "backoff == 1.10",
        "google-cloud-secret-manager == 2.9.2",
        "google-api-core == 1.31.5",
    ],
    packages=find_packages(),
    test_requires=(current / "requirements-test.txt").read_text().splitlines(),
)

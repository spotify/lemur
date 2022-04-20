import pathlib

from setuptools import setup, find_packages

current = pathlib.Path(__file__).resolve().parent

setup(
    name="spotify_gcp_secretmanager",
    entry_points={
        "lemur.plugins": [
            "gcp_secretmanager_dest = plugin_gcp_secretmanager.plugin:GcpSecretManagerDestination",
        ],
    },
    install_requires=[
        "backoff == 1.10",
        "google-cloud-secret-manager == 2.9.2",
        "google-api-core == 1.31.5",
        "googleapis-common-protos == 1.56.0",
    ],
    packages=find_packages(),
    test_requires=(current / "requirements-test.txt").read_text().splitlines(),
)

import pathlib

from setuptools import setup, find_packages

current = pathlib.Path(__file__).resolve().parent

setup(
    name="spotify_dest_gcp",
    entry_points={
        "lemur.plugins": ["gcp_dest = plugin_dest_gcp.plugin:GcpDestination"],
    },
    install_requires=[
        "google-api-python-client >= 1",
        "google-oauth >= 1",
        "backoff >= 1.10",
    ],
    packages=find_packages(),
    test_requires=(current / "requirements-test.txt").read_text().splitlines()
)

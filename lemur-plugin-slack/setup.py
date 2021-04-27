import pathlib

from setuptools import setup, find_packages

current = pathlib.Path(__file__).resolve().parent

setup(
    name="spotify_slack",
    entry_points={
        "lemur.plugins": [
            "slack2_notification = plugin_slack2.plugin:SlackNotification",
        ],
    },
    install_requires=[
        "backoff == 1.10"
    ],
    packages=find_packages(),
)

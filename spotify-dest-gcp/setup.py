from setuptools import setup

setup(
    name='spotify_dest_gcp',
    entry_points={
       'lemur.plugins': [
            'gcp_dest = plugin_dest_gcp.plugin:GcpDestination'
        ],
    },
    install_requires=[
        "google-api-python-client >= 1"
    ],
    test_requires=[
        "pytest"
    ]
)
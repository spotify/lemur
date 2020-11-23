from setuptools import setup

setup(
    name='spotify_dest_gcp',
    entry_points={
       'lemur.plugins': [
            'gcp_dest = plugin_dest_gcp.plugin:GcpDestination'
        ],
    },
)
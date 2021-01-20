from setuptools import setup, find_packages

setup(
    name="lemur_plugin_ffwd",
    version="1.0.0",
    entry_points={
        "lemur.plugins": ["ffwd = lemur_plugin_ffwd.plugin:FFWDMetricPlugin"],
    },
    install_requires=[
        "shumway >= 2.0.0",
    ],
    packages=find_packages()
)

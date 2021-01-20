import json
import requests
import shumway
from requests.exceptions import ConnectionError
from datetime import datetime

from flask import current_app
from lemur.plugins.bases.metric import MetricPlugin


class FFWDMetricPlugin(MetricPlugin):
    title = "Shumway Plugin"
    slug = "ffwd"
    description = "Adds support for sending metrics with Shumway"

    author = "wasabi@spotify.com"
    author_url = "spotify.com"

    def __init__(self, *args, **kwargs):
        self.mr = shumway.MetricRelay("lemur")

    def submit(
        self, metric_name, metric_type, metric_value, metric_tags=None, options=None
    ):
        current_app.logger.debug(
            f"ffwd-plugin: sending metrics {metric_name} {metric_type} {metric_value} {metric_tags}"        )
        self.mr.emit(metric_name, metric_value, tags=metric_tags)

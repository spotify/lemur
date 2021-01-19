import json
import requests
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

    def submit(
        self, metric_name, metric_type, metric_value, metric_tags=None, options=None
    ):
        current_app.logger.warning(
            "ffwd-plugin: not implemented"
        )

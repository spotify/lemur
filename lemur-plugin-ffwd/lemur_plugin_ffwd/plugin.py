import shumway

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

    def filter_tags(self, tags=None):
        if tags:
            return {
                k: v
                for k, v in tags.items()
                if k not in ["task_id", "receiver_hostname", "sender_hostname"]
            }
        return tags

    def submit(self, metric_name, metric_type, metric_value, metric_tags=None, options=None):
        metric_tags = self.filter_tags(metric_tags)
        current_app.logger.debug(
            f"ffwd-plugin: sending metrics {metric_name} {metric_type} {metric_value} {metric_tags}"
        )
        self.mr.emit(metric_name, metric_value, metric_tags)

import logging

import requests
from flask import current_app
from lemur.plugins.base import Plugin
from lemur.plugins.bases import NotificationPlugin

logger = logging.getLogger(__name__)


def _get_token():
    return current_app.config.get("SLACK_BOT_TOKEN")


def _send_notification(data):
    bearer_token = _get_token()
    if not bearer_token:
        logger.warning(
            "SLACK_BOT_TOKEN not set, will not send any Slack notifications."
        )
        return

    res = requests.post(
        "https://slack.com/api/chat.postMessage",
        headers={"Authorization": f"Bearer {bearer_token}"},
        json=data,
    )

    if not res.ok:
        logger.error(
            "Failed to send Slack notification {res.text}",
            extra=dict(result=res.json()),
        )


def _generate_rotation_notification_attachments(endpoint):

    new_cert = endpoint.certificate.replaced[0]
    old_cert = endpoint.certificate

    old_domains = ", ".join([e.name for e in old_cert.domains])
    new_domains = ", ".join([e.name for e in new_cert.domains])

    gcp_project, load_balancer, _ = endpoint.name.split("/")

    old_cert_start_validity = old_cert.not_before.format("YYYY-MM-DD")
    old_cert_end_validity = old_cert.not_after.format("YYYY-MM-DD")

    new_cert_start_validity = new_cert.not_before.format("YYYY-MM-DD")
    new_cert_end_validity = new_cert.not_after.format("YYYY-MM-DD")

    return [
        {
            "color": "#004c99",
            "fallback": f"Rotating certificate {old_cert.name} to {new_cert.name} on {load_balancer}",
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"Rotating certificate on LB `{load_balancer}` in GCP project `{gcp_project}`",
                    },
                },
                {
                    "type": "section",
                    "fields": [
                        {
                            "type": "mrkdwn",
                            "text": f"*Old certificate*\nDomains: {old_domains}\nValidity: {old_cert_start_validity} - {old_cert_end_validity}",
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*New certificate*\nDomains: {new_domains}\nValidity: {new_cert_start_validity} - {new_cert_end_validity}",
                        },
                    ],
                },
            ]
        }
    ]


class SlackNotification(NotificationPlugin):
    title = "Slack Notification"
    slug = "slack2-notification"
    description = "Slack Notification"

    author = "Your Name"
    author_url = "https://github.com/yourname/lemur_pluginname"

    options = [
        {
            "name": "channel",
            "type": "str",
            "required": True,
        },
    ]

    @staticmethod
    def send_rotation_notification(channel, message, endpoint):
        logger.info(f"Sending rotation notification: {channel} {message} {endpoint}")

        attachments = _generate_rotation_notification_attachments(endpoint)

        _send_notification(dict(channel=channel, attachments=attachments))

    @staticmethod
    def send(
        notification_type, message, excluded_targets, options, endpoint=None, **kwargs
    ):
        channel = Plugin.get_option("channel", options)

        if notification_type == "rotation":
            if endpoint is None:
                logger.warning("Received rotation notification but endpoint was None")
                return
            return SlackNotification.send_rotation_notification(
                channel, message, endpoint
            )

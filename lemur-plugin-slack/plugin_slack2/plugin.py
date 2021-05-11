import logging

import backoff
import requests
from flask import current_app
from lemur.plugins.base import Plugin
from lemur.plugins.bases import NotificationPlugin

logger = logging.getLogger(__name__)


def _get_token():
    return current_app.config.get("SLACK_BOT_TOKEN")


@backoff.on_exception(backoff.expo, requests.exceptions.RequestException, max_time=10)
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


def _generate_rotation_notification_attachments(endpoint, extra_message=None):
    new_cert = endpoint.certificate.replaced[0]
    old_cert = endpoint.certificate

    old_domains = ", ".join([e.name for e in old_cert.domains])
    new_domains = ", ".join([e.name for e in new_cert.domains])

    gcp_project, load_balancer, _ = endpoint.name.split("/")

    old_cert_start_validity = old_cert.not_before.format("YYYY-MM-DD")
    old_cert_end_validity = old_cert.not_after.format("YYYY-MM-DD")

    new_cert_start_validity = new_cert.not_before.format("YYYY-MM-DD")
    new_cert_end_validity = new_cert.not_after.format("YYYY-MM-DD")

    # add ping to ATC only if the cert being rotated is a prod (i.e. non-test) cert
    atc_ping = ""
    if "canary-certificate-for-noop.spotify.com" not in new_domains:
        atc_ping += "\n@atc-squad remember to update the list of certs in the deployment manager code!"

    message = f"Rotating certificate on LB `{load_balancer}` in GCP project `{gcp_project}`.{atc_ping}"

    if extra_message:
        message += f": {extra_message}"

    return [
        {
            "color": "#004c99",
            "fallback": message,
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": message,
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

        attachments = _generate_rotation_notification_attachments(endpoint, extra_message=message)

        _send_notification(dict(channel=channel, attachments=attachments))

    @staticmethod
    def send(
        notification_type, message, excluded_targets, options, endpoint=None, **kwargs
    ):
        channel = Plugin.get_option("channel", options)

        try:
            if notification_type == "rotation":
                if endpoint is None:
                    logger.warning("Received rotation notification but endpoint was None")
                    return
                return SlackNotification.send_rotation_notification(
                    channel, message, endpoint
                )
        except Exception as e:
            logger.warning(f"Failed to send Slack notification: {e}")

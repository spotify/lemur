import logging

import requests
from flask import current_app
from lemur.plugins.base import Plugin
from lemur.plugins.bases import NotificationPlugin

logger = logging.getLogger(__name__)


def _get_token():
    return current_app.config.get("SLACK_BOT_TOKEN")


ROTATION_TEMPLATE = """
{
	"text": null,
	"channel": "{{ slack }}",
	"attachments": [{
			"color": "#db0a0a",
			"fallback": " ",
			"blocks": [
				{
					"type": "section",
					"text": {
						"type": "mrkdwn",
						"text": "*Certificate Rotation notification*"
					}
				},
				{
					"type": "divider"
				},
				{
					"type": "section",
					"text": {
						"type": "mrkdwn",
						"text": "*Domain:{{event.data.domain}}*"
					}
				},
				{
					"type": "section",
					"text": {
						"type": "mrkdwn",
						"text": "*Endpoint:{{event.data.endpoint}}*"
					}
				},
				{
					"type": "divider"
				},
				{
					"type": "section",
					"text": {
						"type": "mrkdwn",
						"text": "*Old certificate*"
					}
				},
				{
					"type": "section",
					"text": {
						"type": "mrkdwn",
						"text": "*Validity:*\n{{ event.data.old_cert_validity_start}-{{ event.data.old_cert_validity_end}}"
					}
				},
				{
					"type": "divider"
				},
				{
					"type": "section",
					"text": {
						"type": "mrkdwn",
						"text": "*New certificate*"
					}
				},
				{
					"type": "section",
					"text": {
						"type": "mrkdwn",
						"text": "*Validity:*\n{{ event.data.old_cert_validity_start}-{{ event.data.old_cert_validity_end}}"
					}
				},
				{
					"type": "divider"
				}
			]
}
"""


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


def _generate_rotation_notification(endpoint):
    pass


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

        data = _generate_rotation_notification(endpoint)

        _send_notification(dict(channel=channel, text=data))

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

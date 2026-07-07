from unittest.mock import patch

import pytest
from celery.exceptions import SoftTimeLimitExceeded


@pytest.fixture(autouse=True)
def mock_redis():
    with patch("lemur.common.celery.red"):
        yield


@pytest.fixture(autouse=True)
def no_active_tasks():
    with patch("lemur.common.celery.is_task_active", return_value=False):
        yield


class TestCertificateRotateTask:
    def test_calls_rotate_cli(self, app):
        from lemur.common.celery import certificate_rotate

        with patch("lemur.common.celery.cli_certificate") as mock_cli, \
             patch("lemur.common.celery.metrics"):
            result = certificate_rotate()

            mock_cli.rotate.assert_called_once_with(None, None, None, None, None, True)
            assert result["message"] == "rotation completed"

    def test_passes_notification_config(self, app):
        from lemur.common.celery import certificate_rotate

        app.config["ENABLE_ROTATION_NOTIFICATION"] = True

        with patch("lemur.common.celery.cli_certificate") as mock_cli, \
             patch("lemur.common.celery.metrics"):
            certificate_rotate()

            mock_cli.rotate.assert_called_once_with(None, None, None, None, True, True)

        app.config.pop("ENABLE_ROTATION_NOTIFICATION", None)

    def test_calls_rotate_region_when_region_given(self, app):
        from lemur.common.celery import certificate_rotate

        with patch("lemur.common.celery.cli_certificate") as mock_cli, \
             patch("lemur.common.celery.metrics"):
            certificate_rotate(region="us-east1")

            mock_cli.rotate_region.assert_called_once_with(
                None, None, None, None, True, "us-east1"
            )
            mock_cli.rotate.assert_not_called()

    def test_handles_soft_time_limit(self, app):
        from lemur.common.celery import certificate_rotate

        with patch("lemur.common.celery.cli_certificate") as mock_cli, \
             patch("lemur.common.celery.metrics") as mock_metrics, \
             patch("lemur.common.celery.capture_exception"):
            mock_cli.rotate.side_effect = SoftTimeLimitExceeded()
            result = certificate_rotate()

            assert result is None
            mock_metrics.send.assert_called_once()
            assert "timeout" in mock_metrics.send.call_args[0][0]

    def test_skips_when_already_active(self, app):
        from lemur.common.celery import certificate_rotate

        with patch("lemur.common.celery.is_task_active", return_value=True), \
             patch("lemur.common.celery.cli_certificate") as mock_cli, \
             patch("lemur.common.celery.metrics"), \
             patch("lemur.common.celery.celery_app") as mock_celery:
            mock_celery.current_task.request.id = "test-id"
            result = certificate_rotate()

            mock_cli.rotate.assert_not_called()

    def test_emits_success_metric(self, app):
        from lemur.common.celery import certificate_rotate

        with patch("lemur.common.celery.cli_certificate"), \
             patch("lemur.common.celery.metrics") as mock_metrics:
            certificate_rotate()

            mock_metrics.send.assert_called_once()
            assert "success" in mock_metrics.send.call_args[0][0]


class TestCertificateReissueTask:
    def test_calls_reissue_cli(self, app):
        from lemur.common.celery import certificate_reissue

        with patch("lemur.common.celery.cli_certificate") as mock_cli, \
             patch("lemur.common.celery.metrics"):
            result = certificate_reissue()

            mock_cli.reissue.assert_called_once_with(None, None, True, None)
            assert result["message"] == "reissuance completed"

    def test_passes_notification_config(self, app):
        from lemur.common.celery import certificate_reissue

        app.config["ENABLE_REISSUE_NOTIFICATION"] = True

        with patch("lemur.common.celery.cli_certificate") as mock_cli, \
             patch("lemur.common.celery.metrics"):
            certificate_reissue()

            mock_cli.reissue.assert_called_once_with(None, True, True, None)

        app.config.pop("ENABLE_REISSUE_NOTIFICATION", None)

    def test_handles_soft_time_limit(self, app):
        from lemur.common.celery import certificate_reissue

        with patch("lemur.common.celery.cli_certificate") as mock_cli, \
             patch("lemur.common.celery.metrics") as mock_metrics, \
             patch("lemur.common.celery.capture_exception"):
            mock_cli.reissue.side_effect = SoftTimeLimitExceeded()
            result = certificate_reissue()

            assert result is None
            mock_metrics.send.assert_called_once()
            assert "timeout" in mock_metrics.send.call_args[0][0]

    def test_emits_success_metric(self, app):
        from lemur.common.celery import certificate_reissue

        with patch("lemur.common.celery.cli_certificate"), \
             patch("lemur.common.celery.metrics") as mock_metrics:
            certificate_reissue()

            mock_metrics.send.assert_called_once()
            assert "success" in mock_metrics.send.call_args[0][0]


class TestNotifyExpirationsTask:
    def test_calls_notification_cli(self, app):
        from lemur.common.celery import notify_expirations

        with patch("lemur.common.celery.cli_notification") as mock_cli, \
             patch("lemur.common.celery.metrics"):
            result = notify_expirations()

            mock_cli.expirations.assert_called_once()
            assert result["message"] == "notify for cert expiration"

    def test_passes_exclude_and_disable_config(self, app):
        from lemur.common.celery import notify_expirations

        app.config["EXCLUDE_CN_FROM_NOTIFICATION"] = ["*.test.com"]
        app.config["DISABLE_NOTIFICATION_PLUGINS"] = ["slack"]

        with patch("lemur.common.celery.cli_notification") as mock_cli, \
             patch("lemur.common.celery.metrics"):
            notify_expirations()

            mock_cli.expirations.assert_called_once_with(
                ["*.test.com"], ["slack"]
            )

        app.config.pop("EXCLUDE_CN_FROM_NOTIFICATION", None)
        app.config.pop("DISABLE_NOTIFICATION_PLUGINS", None)

    def test_handles_soft_time_limit(self, app):
        from lemur.common.celery import notify_expirations

        with patch("lemur.common.celery.cli_notification") as mock_cli, \
             patch("lemur.common.celery.metrics") as mock_metrics, \
             patch("lemur.common.celery.capture_exception"):
            mock_cli.expirations.side_effect = SoftTimeLimitExceeded()
            result = notify_expirations()

            assert result is None
            assert "timeout" in mock_metrics.send.call_args[0][0]


class TestCleanAllSourcesTask:
    def test_dispatches_clean_per_source(self, app, session):
        from lemur.common.celery import clean_all_sources
        from lemur.tests.factories import SourceFactory

        s1 = SourceFactory(label="source-a")
        s2 = SourceFactory(label="source-b")
        session.commit()

        with patch("lemur.common.celery.clean_source") as mock_clean, \
             patch("lemur.common.celery.metrics"):
            clean_all_sources()

            labels = [c.args[0] for c in mock_clean.delay.call_args_list]
            assert "source-a" in labels
            assert "source-b" in labels

    def test_emits_success_metric(self, app, session):
        from lemur.common.celery import clean_all_sources

        with patch("lemur.common.celery.clean_source"), \
             patch("lemur.common.celery.metrics") as mock_metrics:
            clean_all_sources()

            mock_metrics.send.assert_called_once()
            assert "success" in mock_metrics.send.call_args[0][0]

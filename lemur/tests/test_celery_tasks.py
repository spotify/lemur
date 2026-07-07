"""Tests for celery tasks.

These tests import lemur.common.celery lazily inside an app context to avoid
the module-level create_app() call that corrupts the session-scoped test DB.
"""
from unittest.mock import patch

from celery.exceptions import SoftTimeLimitExceeded


def _import_celery_task(name):
    """Import a celery task by name, deferring the module load."""
    import lemur.common.celery as mod
    return getattr(mod, name)


class TestCertificateRotateTask:
    def test_calls_rotate_cli(self, app, session):
        with patch("lemur.common.celery.is_task_active", return_value=False), \
             patch("lemur.common.celery.cli_certificate") as mock_cli, \
             patch("lemur.common.celery.metrics"):
            result = _import_celery_task("certificate_rotate")()
            mock_cli.rotate.assert_called_once_with(None, None, None, None, None, True)
            assert result["message"] == "rotation completed"

    def test_passes_notification_config(self, app, session):
        app.config["ENABLE_ROTATION_NOTIFICATION"] = True
        with patch("lemur.common.celery.is_task_active", return_value=False), \
             patch("lemur.common.celery.cli_certificate") as mock_cli, \
             patch("lemur.common.celery.metrics"):
            _import_celery_task("certificate_rotate")()
            mock_cli.rotate.assert_called_once_with(None, None, None, None, True, True)
        app.config.pop("ENABLE_ROTATION_NOTIFICATION", None)

    def test_calls_rotate_region_when_region_given(self, app, session):
        with patch("lemur.common.celery.is_task_active", return_value=False), \
             patch("lemur.common.celery.cli_certificate") as mock_cli, \
             patch("lemur.common.celery.metrics"):
            _import_celery_task("certificate_rotate")(region="us-east1")
            mock_cli.rotate_region.assert_called_once_with(
                None, None, None, None, True, "us-east1"
            )
            mock_cli.rotate.assert_not_called()

    def test_handles_soft_time_limit(self, app, session):
        with patch("lemur.common.celery.is_task_active", return_value=False), \
             patch("lemur.common.celery.cli_certificate") as mock_cli, \
             patch("lemur.common.celery.metrics") as mock_metrics, \
             patch("lemur.common.celery.capture_exception"):
            mock_cli.rotate.side_effect = SoftTimeLimitExceeded()
            result = _import_celery_task("certificate_rotate")()
            assert result is None
            mock_metrics.send.assert_called_once()
            assert "timeout" in mock_metrics.send.call_args[0][0]

    def test_emits_success_metric(self, app, session):
        with patch("lemur.common.celery.is_task_active", return_value=False), \
             patch("lemur.common.celery.cli_certificate"), \
             patch("lemur.common.celery.metrics") as mock_metrics:
            _import_celery_task("certificate_rotate")()
            mock_metrics.send.assert_called_once()
            assert "success" in mock_metrics.send.call_args[0][0]


class TestCertificateReissueTask:
    def test_calls_reissue_cli(self, app, session):
        with patch("lemur.common.celery.is_task_active", return_value=False), \
             patch("lemur.common.celery.cli_certificate") as mock_cli, \
             patch("lemur.common.celery.metrics"):
            result = _import_celery_task("certificate_reissue")()
            mock_cli.reissue.assert_called_once_with(None, None, True, None)
            assert result["message"] == "reissuance completed"

    def test_handles_soft_time_limit(self, app, session):
        with patch("lemur.common.celery.is_task_active", return_value=False), \
             patch("lemur.common.celery.cli_certificate") as mock_cli, \
             patch("lemur.common.celery.metrics") as mock_metrics, \
             patch("lemur.common.celery.capture_exception"):
            mock_cli.reissue.side_effect = SoftTimeLimitExceeded()
            result = _import_celery_task("certificate_reissue")()
            assert result is None
            assert "timeout" in mock_metrics.send.call_args[0][0]

    def test_emits_success_metric(self, app, session):
        with patch("lemur.common.celery.is_task_active", return_value=False), \
             patch("lemur.common.celery.cli_certificate"), \
             patch("lemur.common.celery.metrics") as mock_metrics:
            _import_celery_task("certificate_reissue")()
            mock_metrics.send.assert_called_once()
            assert "success" in mock_metrics.send.call_args[0][0]


class TestNotifyExpirationsTask:
    def test_calls_notification_cli(self, app, session):
        with patch("lemur.common.celery.is_task_active", return_value=False), \
             patch("lemur.common.celery.cli_notification") as mock_cli, \
             patch("lemur.common.celery.metrics"):
            result = _import_celery_task("notify_expirations")()
            mock_cli.expirations.assert_called_once()
            assert result["message"] == "notify for cert expiration"

    def test_handles_soft_time_limit(self, app, session):
        with patch("lemur.common.celery.is_task_active", return_value=False), \
             patch("lemur.common.celery.cli_notification") as mock_cli, \
             patch("lemur.common.celery.metrics") as mock_metrics, \
             patch("lemur.common.celery.capture_exception"):
            mock_cli.expirations.side_effect = SoftTimeLimitExceeded()
            result = _import_celery_task("notify_expirations")()
            assert result is None
            assert "timeout" in mock_metrics.send.call_args[0][0]


class TestCleanAllSourcesTask:
    def test_dispatches_clean_per_source(self, app, session):
        from lemur.tests.factories import SourceFactory

        SourceFactory(label="source-a")
        SourceFactory(label="source-b")
        session.commit()

        with patch("lemur.common.celery.is_task_active", return_value=False), \
             patch("lemur.common.celery.clean_source") as mock_clean, \
             patch("lemur.common.celery.metrics"):
            _import_celery_task("clean_all_sources")()
            labels = [c.args[0] for c in mock_clean.delay.call_args_list]
            assert "source-a" in labels
            assert "source-b" in labels

    def test_emits_success_metric(self, app, session):
        with patch("lemur.common.celery.is_task_active", return_value=False), \
             patch("lemur.common.celery.clean_source"), \
             patch("lemur.common.celery.metrics") as mock_metrics:
            _import_celery_task("clean_all_sources")()
            mock_metrics.send.assert_called_once()
            assert "success" in mock_metrics.send.call_args[0][0]

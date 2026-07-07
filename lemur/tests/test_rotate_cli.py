from unittest.mock import MagicMock, patch, call

import pytest

from lemur.tests.factories import (
    CertificateFactory,
    EndpointFactory,
    SourceFactory,
    UserFactory,
    AuthorityFactory,
)


class TestRequestRotation:
    def test_calls_rotate_certificate_and_sends_notification(self, session, app):
        from lemur.certificates.cli import request_rotation

        old_cert = CertificateFactory()
        new_cert = CertificateFactory()
        source = SourceFactory()
        endpoint = EndpointFactory(source=source, certificate=old_cert)
        session.commit()

        with patch("lemur.certificates.cli.deployment_service") as mock_deploy, \
             patch("lemur.certificates.cli.send_rotation_notification") as mock_notify, \
             patch("lemur.certificates.cli.metrics"):
            request_rotation(endpoint, new_cert, message=True, commit=True)

            mock_deploy.rotate_certificate.assert_called_once_with(endpoint, new_cert)
            mock_notify.assert_called_once_with(new_cert, endpoint=endpoint)

    def test_skips_rotation_without_commit(self, session, app):
        from lemur.certificates.cli import request_rotation

        old_cert = CertificateFactory()
        new_cert = CertificateFactory()
        source = SourceFactory()
        endpoint = EndpointFactory(source=source, certificate=old_cert)
        session.commit()

        with patch("lemur.certificates.cli.deployment_service") as mock_deploy, \
             patch("lemur.certificates.cli.metrics"):
            request_rotation(endpoint, new_cert, message=True, commit=False)

            mock_deploy.rotate_certificate.assert_not_called()

    def test_skips_notification_without_message(self, session, app):
        from lemur.certificates.cli import request_rotation

        new_cert = CertificateFactory()
        source = SourceFactory()
        endpoint = EndpointFactory(source=source)
        session.commit()

        with patch("lemur.certificates.cli.deployment_service"), \
             patch("lemur.certificates.cli.send_rotation_notification") as mock_notify, \
             patch("lemur.certificates.cli.metrics"):
            request_rotation(endpoint, new_cert, message=False, commit=True)

            mock_notify.assert_not_called()

    def test_handles_rotation_error_gracefully(self, session, app):
        from lemur.certificates.cli import request_rotation

        new_cert = CertificateFactory()
        source = SourceFactory()
        endpoint = EndpointFactory(source=source)
        session.commit()

        with patch("lemur.certificates.cli.deployment_service") as mock_deploy, \
             patch("lemur.certificates.cli.metrics") as mock_metrics, \
             patch("lemur.certificates.cli.capture_exception"):
            mock_deploy.rotate_certificate.side_effect = Exception("GCP timeout")
            request_rotation(endpoint, new_cert, message=True, commit=True)

            mock_metrics.send.assert_called_once()
            assert mock_metrics.send.call_args[1]["metric_tags"]["status"] == "failure"

    def test_emits_success_metric(self, session, app):
        from lemur.certificates.cli import request_rotation

        new_cert = CertificateFactory()
        source = SourceFactory()
        endpoint = EndpointFactory(source=source)
        session.commit()

        with patch("lemur.certificates.cli.deployment_service"), \
             patch("lemur.certificates.cli.metrics") as mock_metrics, \
             patch("lemur.certificates.cli.send_rotation_notification"):
            request_rotation(endpoint, new_cert, message=True, commit=True)

            mock_metrics.send.assert_called_once()
            assert mock_metrics.send.call_args[1]["metric_tags"]["status"] == "success"


class TestRotateAllEndpoints:
    """Tests for the bulk rotation path (rotate -o OLD -n NEW) which iterates
    all endpoints on the old cert. This is the path where the list-mutation
    bug lived — old_cert.endpoints is a live SQLAlchemy relationship that gets
    mutated by request_rotation, causing skipped endpoints."""

    def test_rotates_all_endpoints_not_skipping_any(self, session, app):
        """Regression test for the list-mutation bug (PR #83).
        With N endpoints, all N must be rotated."""
        from lemur.certificates.cli import rotate
        from click.testing import CliRunner

        old_cert = CertificateFactory()
        new_cert = CertificateFactory()
        source = SourceFactory()
        endpoints = [EndpointFactory(source=source, certificate=old_cert) for _ in range(6)]
        session.commit()

        rotated_endpoints = []

        def track_rotation(endpoint, certificate):
            rotated_endpoints.append(endpoint.name)
            endpoint.certificate = certificate

        with patch("lemur.certificates.cli.deployment_service") as mock_deploy, \
             patch("lemur.certificates.cli.send_rotation_notification"), \
             patch("lemur.certificates.cli.metrics"):
            mock_deploy.rotate_certificate.side_effect = track_rotation

            runner = CliRunner()
            result = runner.invoke(
                rotate,
                ["-o", old_cert.name, "-n", new_cert.name, "-c"],
                catch_exceptions=False,
            )

            assert result.exit_code == 0, result.output
            assert len(rotated_endpoints) == 6, (
                f"Expected 6 endpoints rotated, got {len(rotated_endpoints)}. "
                f"Rotated: {rotated_endpoints}"
            )

    def test_rotates_single_endpoint_by_name(self, session, app):
        from lemur.certificates.cli import rotate
        from click.testing import CliRunner

        new_cert = CertificateFactory()
        source = SourceFactory()
        endpoint = EndpointFactory(source=source)
        session.commit()

        with patch("lemur.certificates.cli.deployment_service") as mock_deploy, \
             patch("lemur.certificates.cli.send_rotation_notification"), \
             patch("lemur.certificates.cli.metrics"):
            runner = CliRunner()
            result = runner.invoke(
                rotate,
                ["-e", endpoint.name, "-n", new_cert.name, "-c"],
                catch_exceptions=False,
            )

            assert result.exit_code == 0, result.output
            mock_deploy.rotate_certificate.assert_called_once()

    def test_dry_run_does_not_rotate(self, session, app):
        from lemur.certificates.cli import rotate
        from click.testing import CliRunner

        old_cert = CertificateFactory()
        new_cert = CertificateFactory()
        source = SourceFactory()
        EndpointFactory(source=source, certificate=old_cert)
        session.commit()

        with patch("lemur.certificates.cli.deployment_service") as mock_deploy, \
             patch("lemur.certificates.cli.metrics"):
            runner = CliRunner()
            result = runner.invoke(
                rotate,
                ["-o", old_cert.name, "-n", new_cert.name],
                catch_exceptions=False,
            )

            assert result.exit_code == 0
            mock_deploy.rotate_certificate.assert_not_called()

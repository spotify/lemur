import base64
import datetime
import json
import logging
import os
import secrets
import string
import sys
from celery.task.schedules import crontab


CORS = os.environ.get("CORS") == "True"
DEBUG = True


def JsonFormatter(fields=None, **kwargs):
    """Returns a loggin Formatter class to produce json logs that are compatible 
    with GCP Stackdriver. The log output will only contain the fields 
    'timestamp', 'message' as well as `exec_info` and `stack_info` if present,
    and additionaly fields specified by the `fields` parameter.
    These additional fields can be re-named by passing in the field name and the 
    new name as keyword arguments.

    Args:
        fields (Optional[List[str]]): Additional fields that should show up in 
        the log output. Defaults to None.

    Returns:
        class: logging formatter class 
    """
    class _cls(logging.Formatter):
        def __init__(self):
            super().__init__()

        def format(self, record):
            if fields:
                # filter for fields and rename if they are specified as keyword
                # arguments
                data = {
                    kwargs.get(k, k): v
                    for k, v in record.__dict__.items()
                    if k in fields
                }
            else:
                data = {}

            data["timestamp"] = datetime.datetime.now().isoformat()
            data["message"] = record.getMessage()

            if record.exc_info:
                data["exc_info"] = self.formatException(record.exc_info)

            if record.stack_info:
                data["stack_info"] = self.formatStack(record.stack_info)

            return json.dumps(data)

    return _cls


def get_random_secret(length):
    """Creates a cryptographically strong random string of the specified 
    length. It will contain at least one character from each character class 
    (lower, upper, digit, special chars) to conform with legacy password 
    policies.

    Args:
        length (int): length of the secret (number of characters) 

    Returns:
        str: cryptographically strong random string of the specified length
    """
    special_chars = "~!@#$%^&*()_+"
    alphabet = string.ascii_letters + string.digits + special_chars
    while True:
        secret = "".join(secrets.choice(alphabet) for i in range(length))
        if (
            any(c.islower() for c in secret)
            and any(c.isupper() for c in secret)
            and any(c.isdigit() for c in secret)
            and any(c in special_chars for c in secret)
        ):
            break
    return secret


SECRET_KEY = repr(os.environ.get('SECRET_KEY', get_random_secret(32).encode('utf8')))

LEMUR_TOKEN_SECRET = repr(os.environ.get('LEMUR_TOKEN_SECRET',
                                         base64.b64encode(get_random_secret(32).encode('utf8'))))
LEMUR_ENCRYPTION_KEYS = repr(os.environ.get('LEMUR_ENCRYPTION_KEYS',
                                            base64.b64encode(get_random_secret(32).encode('utf8'))))

LEMUR_ALLOWED_DOMAINS = []

LEMUR_EMAIL = ''
LEMUR_SECURITY_TEAM_EMAIL = []

ALLOW_CERT_DELETION = os.environ.get('ALLOW_CERT_DELETION') == "True"

LEMUR_DEFAULT_COUNTRY = str(os.environ.get('LEMUR_DEFAULT_COUNTRY',''))
LEMUR_DEFAULT_STATE = str(os.environ.get('LEMUR_DEFAULT_STATE',''))
LEMUR_DEFAULT_LOCATION = str(os.environ.get('LEMUR_DEFAULT_LOCATION',''))
LEMUR_DEFAULT_ORGANIZATION = str(os.environ.get('LEMUR_DEFAULT_ORGANIZATION',''))
LEMUR_DEFAULT_ORGANIZATIONAL_UNIT = str(os.environ.get('LEMUR_DEFAULT_ORGANIZATIONAL_UNIT',''))

PLUGINS = [
    'email_notification',
    'java_truststore_export',
    'java_keystore_export',
    'openssl_export',
    'cryptography_issuer',
    'digicert_issuer',
    'csr_export',
    'ffwd',
    'gcp_dest',
    'gcp_source',
    'slack2_notification',
    'gcp_secretmanager_dest',
]

LEMUR_DEFAULT_ISSUER_PLUGIN = 'digicert_issuer'
LEMUR_DEFAULT_AUTHORITY = 'digicert' 

METRIC_PROVIDERS = ['ffwd']

ACTIVE_PROVIDERS = ['google']

GOOGLE_CLIENT_ID = str(os.environ.get('GOOGLE_CLIENT_ID','421791425557-lfk56lqi3rnhi4n2fr2rakmbv4lbc93l.apps.googleusercontent.com'))
GOOGLE_SECRET = str(os.environ.get('GOOGLE_SECRET',''))

# disable password login for all but the admin user (as backup in case oauth does not work)
PASSWORD_LOGIN_ALLOWED = ['admin', 'lemur']

USE_ASYNCHRONOUS_DESTINATION_UPLOAD = True

LOG_CONFIG_DICT = dict(
    version=1,
    root={
        "level": "DEBUG",
        "handlers": ["console"]
    },
    loggers={
        "gunicorn.access": {"propagate": False},
        "gunicorn.error": {"propagate": True},
        "uvicorn.error": {"propagate": True},
        "uvicorn.access": {"propagate": False},
    },
    handlers={
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "json",
            "stream": sys.stdout,
        },
    },
    formatters={
        "generic": {
            "format": "%(asctime)s [%(process)d] [%(levelname)s] %(name)s: %(message)s",
            "datefmt": "[%Y-%m-%d %H:%M:%S %z]",
            "class": "logging.Formatter",
        },
        "json": {
            "()": JsonFormatter(
                fields=[
                    "levelname",
                    "name",
                    "source",
                    "task_id",
                    "result",
                    "certificate",
                    "certificate_id",
                    "destination_id",
                    "destination",
                    "num_subtasks_created"
                ],
                levelname="severity",
                name="log",
            )
        },
    },
    disable_existing_loggers=False,
)

SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI','postgresql://lemur:lemur@host.docker.internal:5432/lemur')

# DigiCert Plugin (CertCentral, API v2)
DIGICERT_URL = "https://www.digicert.com"
DIGICERT_API_KEY = os.environ.get("DIGICERT_API_KEY")
DIGICERT_ORG_ID = "130680"
DIGICERT_ORDER_TYPE = "ssl"
DIGICERT_ROOT = """-----BEGIN CERTIFICATE-----
MIIDrzCCApegAwIBAgIQCDvgVpBCRrGhdWrJWZHHSjANBgkqhkiG9w0BAQUFADBh
MQswCQYDVQQGEwJVUzEVMBMGA1UEChMMRGlnaUNlcnQgSW5jMRkwFwYDVQQLExB3
d3cuZGlnaWNlcnQuY29tMSAwHgYDVQQDExdEaWdpQ2VydCBHbG9iYWwgUm9vdCBD
QTAeFw0wNjExMTAwMDAwMDBaFw0zMTExMTAwMDAwMDBaMGExCzAJBgNVBAYTAlVT
MRUwEwYDVQQKEwxEaWdpQ2VydCBJbmMxGTAXBgNVBAsTEHd3dy5kaWdpY2VydC5j
b20xIDAeBgNVBAMTF0RpZ2lDZXJ0IEdsb2JhbCBSb290IENBMIIBIjANBgkqhkiG
9w0BAQEFAAOCAQ8AMIIBCgKCAQEA4jvhEXLeqKTTo1eqUKKPC3eQyaKl7hLOllsB
CSDMAZOnTjC3U/dDxGkAV53ijSLdhwZAAIEJzs4bg7/fzTtxRuLWZscFs3YnFo97
nh6Vfe63SKMI2tavegw5BmV/Sl0fvBf4q77uKNd0f3p4mVmFaG5cIzJLv07A6Fpt
43C/dxC//AH2hdmoRBBYMql1GNXRor5H4idq9Joz+EkIYIvUX7Q6hL+hqkpMfT7P
T19sdl6gSzeRntwi5m3OFBqOasv+zbMUZBfHWymeMr/y7vrTC0LUq7dBMtoM1O/4
gdW7jVg/tRvoSSiicNoxBN33shbyTApOB6jtSj1etX+jkMOvJwIDAQABo2MwYTAO
BgNVHQ8BAf8EBAMCAYYwDwYDVR0TAQH/BAUwAwEB/zAdBgNVHQ4EFgQUA95QNVbR
TLtm8KPiGxvDl7I90VUwHwYDVR0jBBgwFoAUA95QNVbRTLtm8KPiGxvDl7I90VUw
DQYJKoZIhvcNAQEFBQADggEBAMucN6pIExIK+t1EnE9SsPTfrgT1eXkIoyQY/Esr
hMAtudXH/vTBH1jLuG2cenTnmCmrEbXjcKChzUyImZOMkXDiqw8cvpOp/2PV5Adg
06O/nVsJ8dWO41P0jmP6P6fbtGbfYmbW0W5BjfIttep3Sp+dWOIrWcBAI+0tKIJF
PnlUkiaY4IBIqDfv8NZ5YBberOgOzW6sRBc4L0na4UU+Krk2U886UAb3LujEV0ls
YSEY1QSteDwsOoBrp+uvFRTp2InBuThs4pFsiv9kuXclVzDAGySj4dzp30d8tbQk
CAUw7C29C79Fv1C5qfPrmAESrciIxpg0X40KPMbp1ZWVbd4=
-----END CERTIFICATE-----"""

REDIS_PASSWORD = os.environ.get("REDIS_PASSWORD")
REDIS_HOST = os.environ.get("REDIS_HOST", "lemur-redis.services.gew1.spotify.net")
REDIS_PORT = os.environ.get("REDIS_PORT", "6379")
REDIS_DB = os.environ.get("REDIS_DB", "0")

CELERY_RESULT_BACKEND = f"redis://:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}"
CELERY_BROKER_URL = CELERY_RESULT_BACKEND
CELERY_IMPORTS = "lemur.common.celery"
CELERY_TIMEZONE = "UTC"
CELERYD_HIJACK_ROOT_LOGGER = False if LOG_CONFIG_DICT else True

# increase visibility timeout (should be longer than longest skew-chain)
# see: https://docs.celeryproject.org/en/2.2/getting-started/brokers/redis.html#visibility-timeout
BROKER_TRANSPORT_OPTIONS = {'visibility_timeout': 21600, 'health_check_interval': 5}  # 6 hours

CELERYBEAT_SCHEDULE = {
    'certificate_reissue': {
        'task': 'lemur.common.celery.certificate_reissue',
        'options': {
            'expires': 180
        },
        'schedule': crontab(
            day_of_week='mon-thu', 
            hour="7", 
            minute="00"
        ), # 09:00 CEST on Mon,Tue,Wed,Thu
    },
    'rotate_all_pending_endpoints': {
        'task': 'lemur.common.celery.rotate_all_pending_endpoints',
        'options': {
            'expires': 180
        },
        'schedule': crontab(
            day_of_week='mon-thu', 
            hour="12", 
            minute="00"
        ), # 14:00 CEST on Mon,Tue,Wed,Thu
    },
    'fetch_all_pending_certs': {
        'task': 'lemur.common.celery.fetch_all_pending_certs',
        'options': {
            'expires': 180
        },
        'schedule': crontab(minute="*/10"), # every 10 minutes
    },
    'certificate_destination_check': {
        'task': 'lemur.common.celery.create_certificate_check_destination_tasks',
        'options': {
            'expires': 180
        },
        'schedule': crontab(minute="*/10"), # every 10 minutes
    },
    'sync_all_sources': {
        'task': 'lemur.common.celery.sync_all_sources',
        'options': {
            'expires': 180
        },
        'schedule': crontab(minute="*/10"), # every 10 minutes
    },
    'report_endpoint_time_to_expiration': {
        'task': 'lemur.common.celery.report_endpoint_time_to_expiration',
        'options': {
            'expires': 180
        },
        'schedule': crontab(minute="*/30"), # every 30 minutes
    },
    'report_unresolved_pending_certificates_age': {
        'task': 'lemur.common.celery.report_unresolved_pending_certificates_age',
        'options': {
            'expires': 180
        },
        'schedule': crontab(minute="*/30"), # every 30 minutes
    },
}

# how many seconds to wait between rotating the certificate on each load balancer
CELERY_ROTATE_ENDPOINT_SKEW = {
    "start": 0,  # execute first rotate endpoint task immediately
    "step": 600,  # wait 10 minutes in between all subsequent rotations
    "stop": None,  # no maximum waiting time
}

# how many seconds to wait between attaching a new cert to a load balancer and detaching the old one
CELERY_ROTATE_ENDPOINT_DELAY_BEFORE_DETACH = 300  # 5 minutes

USE_GCP_CERTIFICATE_NAMES = True

SLACK_BOT_TOKEN = os.environ.get("SLACK_BOT_TOKEN")

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
debug = True


def JsonFormatter(fields=None, **kwargs):
    class _cls(logging.Formatter):
        def __init__(self):
            super().__init__()

        def format(self, record):
            if fields:
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
    'slack_notification',
    'java_truststore_export',
    'java_keystore_export',
    'openssl_export',
    'cryptography_issuer',
    'digicert_issuer',
    'csr_export',
    'ffwd',
    'gcp_dest',
]

LEMUR_DEFAULT_ISSUER_PLUGIN = 'digicert_issuer'
LEMUR_DEFAULT_AUTHORITY = 'digicert' 

METRIC_PROVIDERS = ['ffwd']

ACTIVE_PROVIDERS = ['google']

GOOGLE_CLIENT_ID = str(os.environ.get('GOOGLE_CLIENT_ID','421791425557-lfk56lqi3rnhi4n2fr2rakmbv4lbc93l.apps.googleusercontent.com'))
GOOGLE_SECRET = str(os.environ.get('GOOGLE_SECRET',''))

LOG_LEVEL = str(os.environ.get('LOG_LEVEL','DEBUG'))
LOG_FILE = str(os.environ.get('LOG_FILE','lemur.log'))
LOG_CONFIG_DICT = dict(
    version=1,
    root={"level": "INFO", "handlers": ["console"]},
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
                fields=["levelname", "name"],
                levelname="severity",
                name="log",
            )
        },
    },
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

CELERYBEAT_SCHEDULE = {
    'fetch_all_pending_certs': {
        'task': 'lemur.common.celery.fetch_all_pending_certs',
        'options': {
            'expires': 180
        },
        'schedule': crontab(minute="*/5"), # every 5 minutes
    },
    'certificate_reissue': {
        'task': 'lemur.common.celery.certificate_reissue',
        'options': {
            'expires': 180
        },
        'schedule': crontab(minute="47"), # once per hour
    },
}

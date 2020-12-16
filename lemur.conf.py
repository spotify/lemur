import os
import random
import string
import base64
from ast import literal_eval

_basedir = os.path.abspath(os.path.dirname(__file__))

CORS = os.environ.get("CORS") == "True"
debug = True


def get_random_secret(length):
    secret_key = "".join(
        random.choice(string.ascii_uppercase) for x in range(round(length / 4))
    )
    secret_key = secret_key + "".join(
        random.choice("~!@#$%^&*()_+") for x in range(round(length / 4))
    )
    secret_key = secret_key + "".join(
        random.choice(string.ascii_lowercase) for x in range(round(length / 4))
    )
    return secret_key + "".join(
        random.choice(string.digits) for x in range(round(length / 4))
    )


SECRET_KEY = repr(os.environ.get("SECRET_KEY", get_random_secret(32).encode("utf8")))

LEMUR_TOKEN_SECRET = repr(
    os.environ.get(
        "LEMUR_TOKEN_SECRET", base64.b64encode(get_random_secret(32).encode("utf8"))
    )
)
LEMUR_ENCRYPTION_KEYS = repr(
    os.environ.get(
        "LEMUR_ENCRYPTION_KEYS", base64.b64encode(get_random_secret(32).encode("utf8"))
    )
)

LEMUR_ALLOWED_DOMAINS = []

LEMUR_EMAIL = ""
LEMUR_SECURITY_TEAM_EMAIL = []

ALLOW_CERT_DELETION = os.environ.get("ALLOW_CERT_DELETION") == "True"

LEMUR_DEFAULT_COUNTRY = str(os.environ.get("LEMUR_DEFAULT_COUNTRY", ""))
LEMUR_DEFAULT_STATE = str(os.environ.get("LEMUR_DEFAULT_STATE", ""))
LEMUR_DEFAULT_LOCATION = str(os.environ.get("LEMUR_DEFAULT_LOCATION", ""))
LEMUR_DEFAULT_ORGANIZATION = str(os.environ.get("LEMUR_DEFAULT_ORGANIZATION", ""))
LEMUR_DEFAULT_ORGANIZATIONAL_UNIT = str(
    os.environ.get("LEMUR_DEFAULT_ORGANIZATIONAL_UNIT", "")
)

LEMUR_DEFAULT_ISSUER_PLUGIN = str(os.environ.get("LEMUR_DEFAULT_ISSUER_PLUGIN", ""))
LEMUR_DEFAULT_AUTHORITY = str(os.environ.get("LEMUR_DEFAULT_AUTHORITY", ""))

METRIC_PROVIDERS = []

ACTIVE_PROVIDERS = ["google"]

GOOGLE_CLIENT_ID = str(
    os.environ.get(
        "GOOGLE_CLIENT_ID",
        "421791425557-lfk56lqi3rnhi4n2fr2rakmbv4lbc93l.apps.googleusercontent.com",
    )
)
GOOGLE_SECRET = str(os.environ.get("GOOGLE_SECRET", ""))

LOG_LEVEL = str(os.environ.get("LOG_LEVEL", "DEBUG"))
# LOG_FILE = str(os.environ.get('LOG_FILE','/home/lemur/.lemur/lemur.log'))

SQLALCHEMY_DATABASE_URI = os.environ.get(
    "SQLALCHEMY_DATABASE_URI", "postgresql://lemur:lemur@host.docker.internal:5432/lemur"
)

# DigiCert Plugin (CertCentral, API v2)
DIGICERT_URL = "https://www.digicert.com"
DIGICERT_API_KEY = os.environ.get("DIGICERT_API_KEY")
DIGICERT_ORG_ID = "130680"
DIGICERT_ORDER_TYPE = "ssl_plus"
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

REDIS_HOST = os.environ.get("REDIS_HOST", "host.docker.internal") 
REDIS_PORT = os.environ.get("REDIS_PORT", "6379")
REDIS_DB = os.environ.get("REDIS_DB", "0")

CELERY_RESULT_BACKEND = f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}"
CELERY_BROKER_URL = CELERY_RESULT_BACKEND
CELERY_IMPORTS = "lemur.common.celery"
CELERY_TIMEZONE = "UTC"


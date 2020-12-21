import os
import secrets
import string
import base64
from ast import literal_eval

_basedir = os.path.abspath(os.path.dirname(__file__))

CORS = os.environ.get("CORS") == "True"
debug = True


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

LEMUR_DEFAULT_ISSUER_PLUGIN = str(os.environ.get('LEMUR_DEFAULT_ISSUER_PLUGIN',''))
LEMUR_DEFAULT_AUTHORITY = str(os.environ.get('LEMUR_DEFAULT_AUTHORITY',''))

METRIC_PROVIDERS = []

ACTIVE_PROVIDERS = ['google']

GOOGLE_CLIENT_ID = str(os.environ.get('GOOGLE_CLIENT_ID','421791425557-lfk56lqi3rnhi4n2fr2rakmbv4lbc93l.apps.googleusercontent.com'))
GOOGLE_SECRET = str(os.environ.get('GOOGLE_SECRET',''))

LOG_LEVEL = str(os.environ.get('LOG_LEVEL','DEBUG'))
# LOG_FILE = str(os.environ.get('LOG_FILE','/home/lemur/.lemur/lemur.log'))

SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI','postgresql://lemur:lemur@localhost:5432/lemur')

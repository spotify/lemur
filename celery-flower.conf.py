import os

GOOGLE_CLIENT_ID = str(os.environ.get('GOOGLE_CLIENT_ID','421791425557-lfk56lqi3rnhi4n2fr2rakmbv4lbc93l.apps.googleusercontent.com'))
GOOGLE_SECRET = str(os.environ.get('GOOGLE_SECRET',''))

OAUTH2_KEY=GOOGLE_CLIENT_ID
OAUTH2_SECRET=GOOGLE_SECRET
OAUTH2_REDIRECT_URI="https://certs.spotify.net"

logging = "debug" 
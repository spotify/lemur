#!/bin/bash

python /opt/lemur/celery_flower.py \
  --debug=True \
  --url_prefix=celery-flower \
  --auth=.*@spotify\.com \
  --oauth2_key=421791425557-lfk56lqi3rnhi4n2fr2rakmbv4lbc93l.apps.googleusercontent.com \
  --oauth2_secret=${GOOGLE_SECRET} \
  --oauth2_redirect_uri=https://certs.spotify.net/celery-flower/login \
  --broker=redis://:${REDIS_PASSWORD}@lemur-redis.services.gew1.spotify.net:6379/0
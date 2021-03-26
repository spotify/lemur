#!/bin/bash

flower --conf=/opt/lemur/celery-flower.conf.py --url_prefix=celery-flower --auth=.*@spotify\.com --broker=redis://:${REDIS_PASSWORD}@lemur-redis.services.gew1.spotify.net:6379/0
#!/bin/bash

#flower --broker=redis://:${REDIS_PASSWORD}@lemur-redis.services.gew1.spotify.net:6379/0
flower --conf=celery-flower.conf.py --auth=.*@spotify\.com --broker=redis://:${REDIS_PASSWORD}@localhost:6379/0
#!/usr/bin/env bash
set -ex

LEMUR_ENV=".lemur-env"

if [[ -f "$LEMUR_ENV" ]]; then
    echo "[dev-setup] $LEMUR_ENV already exists, aborting."
    exit 1
fi

echo "[dev-setup] generating environment and saving it to .lemur-env..."
docker run -it --rm gcr.io/xpn-cert-management/spotify-lemur:latest \
    sh -c "lemur create_config > /dev/null 2>&1 && cat ~/.lemur/lemur.conf.py | grep -E 'SECRET_KEY|LEMUR_TOKEN_SECRET|LEMUR_ENCRYPTION_KEYS' | sed 's/['\'' ]//g'" \
    > $LEMUR_ENV

LOCALHOST="host.docker.internal" 
# # if you're on linux, uncomment these lines to avoid resolve issues
# # (see https://stackoverflow.com/questions/48546124/what-is-linux-equivalent-of-host-docker-internal)
# LOCALHOST="172.17.0.1"
echo SQLALCHEMY_DATABASE_URI="postgresql://lemur:lemur@${LOCALHOST}:5432/lemur" >> .lemur-env
echo REDIS_HOST=${LOCALHOST} >> .lemur-env

echo "[dev-setup] initializing database..."
docker run -it --rm \
    -v $(pwd)/lemur.conf.py:/app/lemur.conf.py \
    --env-file $LEMUR_ENV \
    -e LEMUR_CONF="/app/lemur.conf.py" \
    -w /app/lemur \
    gcr.io/xpn-cert-management/spotify-lemur:latest \
    lemur init

echo "[dev-setup] done!"


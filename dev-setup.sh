#!/usr/bin/env bash
set -ex

LEMUR_ENV=".lemur-env"
LOCALHOST="host.docker.internal"
# Set LOCALHOST for linux to fix resolve issue
# (see https://stackoverflow.com/questions/48546124/what-is-linux-equivalent-of-host-docker-internal)
if [ "$(uname)" == "Linux" ]; then
    LOCALHOST="172.17.0.1"
fi

if [[ -f "$LEMUR_ENV" ]]; then
    echo "[dev-setup] $LEMUR_ENV already exists, aborting."
    exit 1
fi

echo "[dev-setup] build lemur dev-setup container"
docker build -t spotify-lemur-dev-setup -f Dockerfile.dev-setup .

echo "[dev-setup] generating environment and saving it to .lemur-env..."
docker run -it --rm spotify-lemur-dev-setup \
    sh -c "lemur create_config > /dev/null 2>&1 && cat ~/.lemur/lemur.conf.py | grep -E 'SECRET_KEY|LEMUR_TOKEN_SECRET|LEMUR_ENCRYPTION_KEYS' | sed 's/['\'' ]//g'" \
    > $LEMUR_ENV

echo "[dev-setup] starting only postgres container in docker-compose"
POSTGRES_PASSWORD=lemur docker-compose up -d postgres

echo "[dev-setup] set local database and redis URLs"
echo SQLALCHEMY_DATABASE_URI="postgresql://lemur:lemur@${LOCALHOST}:5432/lemur" >> .lemur-env
echo REDIS_HOST=${LOCALHOST} >> .lemur-env

echo "[dev-setup] initializing database..."
docker run -it --rm \
    -v $(pwd)/lemur.conf.py:/app/lemur.conf.py \
    --env-file $LEMUR_ENV \
    -e LEMUR_CONF="/app/lemur.conf.py" \
    -w /app/lemur \
    spotify-lemur-dev-setup \
    lemur init

echo "[dev-setup] stopping postgres container"
docker-compose stop postgres

echo "[dev-setup] done!"

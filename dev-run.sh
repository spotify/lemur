#!/bin/bash

echo "Reading local environment variables from .lemur-env"
source .lemur-env

echo "Starting postgres..."
docker-compose up -d postgres

echo "Starting redis..."
docker-compose up -d redis

if [[ `uname` == 'Linux' ]]; then
    echo "Starting nginx for Linux..."
    docker-compose up -d nginx-linux
else
    echo "Starting nginx for Mac..."
    docker-compose up -d nginx-mac
fi

echo "Starting celery worker, beat scheduler and flower..."

celery -A lemur.common.celery worker --loglevel=debug --concurrency 1 -E &

celery -A lemur.common.celery beat --loglevel=debug &

celery flower --broker=redis://:lemur@localhost:6379/0 &

echo "You can see postgres, nginx and redis logs by running"
echo "  docker-compose logs -f"
echo "Your local Celery flower is running on http://localhost:5555"

echo "Starting the Lemur backend..."
lemur runserver

echo "run   docker-compose stop   to shutdown the local database, ngnix and redis"
echo "and   killall celery        to shutdown the local celery instances."


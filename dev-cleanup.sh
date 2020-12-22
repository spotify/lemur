#!/bin/bash

echo -n "Really delete the database and your local config .lemur-env? (y/n)?"
read a
if [ "$a" == "${a#[Yy]}" ] ;then
    echo "Cancelled (didn't delete anything, promise)."; exit 0
fi

set -x

docker-compose rm -f postgres
docker-compose rm -f redis
docker volume rm spotify-lemur_pgdata

rm .lemur-env
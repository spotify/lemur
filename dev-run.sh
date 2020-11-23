#!/usr/bin/env sh
docker run -it --rm \
    --env-file .lemur-env \
    -p 8080:80 \
    spotify-lemur
#!/usr/bin/env sh
docker run -it --rm \
    -v $HOME/.config/gcloud/application_default_credentials.json:/root/.config/gcloud/application_default_credentials.json \
    --env-file .lemur-env \
    -p 8080:80 \
    spotify-lemur
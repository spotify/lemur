#!/usr/bin/env sh

# to run: ./lemur-cli.sh certificate reissue
docker run -it --rm -v $HOME/.config/gcloud/application_default_credentials.json:/root/.config/gcloud/application_default_credentials.json --env-file .lemur-env spotify-lemur lemur $@
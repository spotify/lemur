#!/bin/bash

sed 's/gcr\.io\/xpn-cert-management\/lemur/lemur-local-dev/' Dockerfile > Dockerfile.local-dev

docker build -t spotify-lemur -f Dockerfile.local-dev .
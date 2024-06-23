#!/bin/bash

set -e

repo="rsundqvist/time-split"
today="${repo}:$(date --iso-8601)"
latest="${repo}:latest"

docker build . -t "$latest"
docker tag "$today" "$latest"

docker push "$today"
docker push "$latest"

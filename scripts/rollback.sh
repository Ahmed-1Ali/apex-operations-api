#!/usr/bin/env sh
set -eu
if [ "$#" -ne 1 ]; then echo "Usage: $0 <known-good-version>" >&2; exit 2; fi
export APP_VERSION="$1"
docker compose up -d --no-build --pull never api
docker compose ps
echo "Rollback requested to prebuilt image version: $APP_VERSION"

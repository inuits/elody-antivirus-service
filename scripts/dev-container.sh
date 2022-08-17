#!/bin/bash

__DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

DOCKER=docker
if [ -x "$(command -v podman)" ]; then
  DOCKER=podman
fi

${DOCKER} run -it --rm -v ${__DIR}/api:/app/api -p 8003:8003 inuits-dams-csv-import-service:dev $@

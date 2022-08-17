#!/bin/bash
DOCKER=docker
if [ -x "$(command -v podman)" ]; then
  DOCKER=podman
fi

${DOCKER} run -it --rm -p 8003:8003 --env APP_ENV=production inuits-dams-csv-import-service:latest $@

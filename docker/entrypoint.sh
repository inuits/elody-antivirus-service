#!/bin/sh

set -e

if [ ! -z "$@" ]; then
  echo "Running command: $@"
  exec $@
  exit $?
fi

if [ ! -z "$TRUSTED_CA_BUNDLE" ]; then
  cp /etc/ssl/certs/ca-certificates.crt /tmp/ca-certificates.crt
  echo "${TRUSTED_CA_BUNDLE}" >> /tmp/ca-certificates.crt
  export CURL_CA_BUNDLE="/tmp/ca-certificates.crt"
fi

/usr/sbin/clamd

if [ "$APP_ENV" = "dev" ]; then
  echo "Starting development server..."
  export FLASK_DEBUG='1'
  cd /app/api
  exec /usr/local/bin/flask run --host=0.0.0.0
else
  echo "Starting gunicorn server..."
  cd /app/api
  exec /usr/local/bin/gunicorn -b 0.0.0.0 --timeout 0 --workers=1 "app:app"
fi

### Base stage
FROM python:3.10-alpine AS base-stage

RUN apk update && apk add --no-cache clamav clamav-libunrar clamav-daemon \
	&& mkdir -p /var/run/clamav \
	&& chown -R clamav:clamav /var/run/clamav \
    && mkdir -p /var/log/clamav \
    && chown -R clamav:clamav /var/log/clamav \
    && freshclam

ENV FLASK_APP=app.py

COPY docker/entrypoint*.sh /
COPY requirements.txt ./
COPY requirements_dev.txt ./

ENTRYPOINT ["/entrypoint.sh"]

### Development stage
FROM base-stage AS development-stage

ENV APP_ENV=dev

COPY docker/pip.conf /etc

RUN pip install --no-cache-dir -r requirements.txt -r requirements_dev.txt

EXPOSE 5000

### Build stage
FROM base-stage AS build-stage

COPY docker/pip.conf /etc
COPY api /app/api

RUN pip install --no-cache-dir -r requirements.txt

### Production stage
FROM base-stage AS production-stage

ENV APP_ENV=prod

COPY --from=build-stage / /

ENV GUNICORN_CMD_ARGS="--workers=3"

EXPOSE 8000

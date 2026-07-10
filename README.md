<p align="center">
  <a href="https://elody.eu"><img src="https://elody.eu/images/logo.svg" alt="Elody" width="96" /></a>
</p>

<p align="center">Part of <a href="https://elody.eu">Elody</a> — the open semantic data platform.</p>

# Inuits DAMS Antivirus Service

Event-driven Flask service that scans uploaded mediafiles with [ClamAV](https://www.clamav.net/) and publishes the result back onto RabbitMQ. No public HTTP surface beyond `/health` — everything runs off AMQP.

## Flow

```
storage-api  ──"dams.file_uploaded"──►  antivirus-service  ──ClamAV──► scan result
                                              │
                                              └──"dams.file_scanned"──► collection-api / consumers
```

1. Something (storage-api, an importer) uploads a mediafile and publishes `dams.file_uploaded`.
2. This service consumes the event, fetches the file, streams it through the ClamAV daemon.
3. It publishes `dams.file_scanned` with `{ mediafile_id, clamav_version, infected, filename }` so downstream services can quarantine or promote the file.
4. On the `dams.update_clamav` routing key the service refreshes ClamAV's signature database.

## RabbitMQ topics consumed

| Routing key | Queue | Handler |
|-------------|-------|---------|
| `dams.file_uploaded` (and friends) | `scan.uploaded.file` | `scan_uploaded_file` — runs the scan, publishes `dams.file_scanned`. |
| `dams.update_clamav` | `update.clamav.version` | `update_clamav_version` — triggers a signature refresh. |

Routing-key prefix (`dams` by default) is set via `ROUTING_KEY_PREFIX`. Queue type is quorum by default (`QUEUE_TYPE`).

## HTTP endpoints

| Method | Path | Purpose |
|--------|------|---------|
| `GET` | `/health` | Liveness probe; also verifies the RabbitMQ connection when `HEALTH_CHECK_EXTERNAL_SERVICES=true`. |

## Layout

- `api/app.py` — Flask bootstrap, health check, RabbitMQ init.
- `api/queues.py` — AMQP consumer declarations (see routing-key table above).
- `api/scanner.py` — ClamAV integration (`pyclamd`) and result publishing.
- `api/rabbit.py` — AMQP client wiring.
- `docker/` — container build; includes the ClamAV daemon.
- `scripts/` — operational helpers.

## Local setup

The [elody-common](https://gitlab.inuits.io/rnd/inuits/elody/elody-common) repository ships the shared docker-compose stack. Enable this service via `docker-compose-include-antivirus-service.yml`.

## Dependencies

Python 3, Flask (for `/health` only), `pyclamd`, `cloudevents`, RabbitMQ client. Container also ships the ClamAV daemon. Full pin list in `requirements.txt`.

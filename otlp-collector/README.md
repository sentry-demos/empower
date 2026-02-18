# OTLP Collector

OpenTelemetry Collector that forwards OTLP data to SENTRY_ORG using [Sentry Exporter](https://github.com/open-telemetry/opentelemetry-collector-contrib/tree/main/exporter/sentryexporter).

## Sentry project routing

The exporter maps `service.name` to a Sentry project slug. Each sending app sets its own `service.name` (e.g. `staging-otlp-collector-flask`), typically by simply setting a special environment variable `OTEL_SERVICE_NAME`. The Sentry project with that slug must exist, or enable `auto_create_projects: true` in `config.yaml`.

FROM otel/opentelemetry-collector-contrib:0.145.0

COPY config.yaml /etc/otelcol-contrib/config.yaml

EXPOSE 8080

ENTRYPOINT ["/otelcol-contrib", "--config=/etc/otelcol-contrib/config.yaml"]

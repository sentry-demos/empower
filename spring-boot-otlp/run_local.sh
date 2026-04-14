#!/bin/bash

set -e

# Store agent JAR outside of target/ so it survives 'mvn clean'
SENTRY_OTEL_AGENT_VERSION="8.28.0"
AGENT_DIR="./lib"
AGENT_JAR="sentry-opentelemetry-agent-${SENTRY_OTEL_AGENT_VERSION}.jar"
AGENT_PATH="${AGENT_DIR}/${AGENT_JAR}"

# Download the agent if not present
if [ ! -f "${AGENT_PATH}" ]; then
  echo "Downloading Sentry OpenTelemetry Agent ${SENTRY_OTEL_AGENT_VERSION}..."
  mkdir -p "${AGENT_DIR}"
  curl -L -o "${AGENT_PATH}" \
    "https://repo1.maven.org/maven2/io/sentry/sentry-opentelemetry-agent/${SENTRY_OTEL_AGENT_VERSION}/${AGENT_JAR}"
fi

function cleanup {
  stop.sh java $SPRINGBOOTOTLP_LOCAL_PORT 
}
trap cleanup EXIT

# Configure OpenTelemetry agent with Sentry
# SENTRY_AUTO_INIT=false lets Spring Boot's Sentry integration handle initialization
# OTEL_*_EXPORTER=none disables default OTLP exporters (Sentry handles exporting)
export SENTRY_AUTO_INIT=false
export OTEL_TRACES_EXPORTER=none
export OTEL_METRICS_EXPORTER=none
export OTEL_LOGS_EXPORTER=none

# Run with the OpenTelemetry agent
JAVA_TOOL_OPTIONS="-javaagent:${AGENT_PATH}" \
  ./mvnw clean spring-boot:run -Dspring-boot.run.arguments=--server.port=$SPRINGBOOTOTLP_LOCAL_PORT

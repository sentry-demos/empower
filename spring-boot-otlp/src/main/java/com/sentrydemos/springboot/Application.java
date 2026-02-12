package com.sentrydemos.springboot;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.context.annotation.Bean;

import org.springframework.web.client.RestClient;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

//run with ./mvnw spring-boot:run in the spring-boot directory

@SpringBootApplication
public class Application {

	private static final Logger logger = LoggerFactory.getLogger(Application.class);
	
	public static void main(String[] args) {
		String serviceName = System.getProperty("otel.service.name", System.getenv().getOrDefault("OTEL_SERVICE_NAME", ""));
		String collectorUrl = System.getenv().getOrDefault("OTEL_EXPORTER_OTLP_ENDPOINT", "");
		if (!serviceName.isEmpty() && collectorUrl.isEmpty()) {
			throw new IllegalStateException("OTEL_SERVICE_NAME is set but OTEL_EXPORTER_OTLP_ENDPOINT is empty");
		}
		SpringApplication.run(Application.class, args);
	}

	@Bean
	RestClient restClient() {
		return RestClient.create();
	}

	// Note: With OpenTelemetry integration, sampling is controlled via:
	// - sentry.traces-sample-rate in application.properties
	// - OpenTelemetry's native sampling mechanisms
	// The Sentry TracesSamplerCallback is not used with OpenTelemetry agent.
}

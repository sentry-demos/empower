package com.sentrydemos.springboot;

import java.sql.Date;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.Bean;

import org.springframework.web.client.RestClient;

import io.sentry.Sentry;

import io.sentry.SentryOptions.TracesSamplerCallback;
import io.sentry.SamplingContext;
import io.sentry.CustomSamplingContext;
import org.springframework.stereotype.Component;
import jakarta.servlet.http.HttpServletRequest;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

//run with ./mvnw spring-boot:run in the spring-boot directory

@SpringBootApplication
public class Application {

	private static final Logger logger = LoggerFactory.getLogger(Application.class);
	
	public static void main(String[] args) {
		SpringApplication.run(Application.class, args);
	}

	@Bean
	RestClient restClient() {
		return RestClient.create();
	}

	@Component
	class CustomTracesSamplerCallback implements TracesSamplerCallback {
	@Override
		public Double sample(SamplingContext context) {

			CustomSamplingContext customSamplingContext = context.getCustomSamplingContext();

			HttpServletRequest request = (HttpServletRequest) customSamplingContext.get("request");

			if (customSamplingContext != null) {
				if (request.getMethod().equals("OPTIONS")) {
					return 0.0;
				}
			}
			return 1.0;
		}
	}
}


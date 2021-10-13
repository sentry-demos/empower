package com.sentrydemos.springboot;

import java.sql.Date;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.context.annotation.Bean;

import io.sentry.Sentry;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

//run with ./mvnw spring-boot:run in the spring-boot directory

@SpringBootApplication
public class Application {
	
	@Value("${sentry.dsn}")
	private String sentryDSN; //value comes from the application.properties's sentry.dsn (value is also used with Logback)
	
	private static final Logger logger = LoggerFactory.getLogger(Application.class);
	
	public static void main(String[] args) {
		SpringApplication.run(Application.class, args);
	}

	// sentry properties configured here for Java Spring Boot
	// https://docs.sentry.io/platforms/java/guides/spring-boot/logging-frameworks/	
	@Bean
	public void initSentry() {
		logger.info("Initializing Sentry...");
		
		Sentry.init(options -> {
			options.setDsn(sentryDSN);
			String environment = ((System.getenv("SPRINGBOOT_ENV") == null) ? "production" : System.getenv("SPRINGBOOT_ENV"));
			options.setEnvironment(environment);
			options.setTracesSampleRate(1.0);
			options.setRelease(getRelease());
		});
	}

	@SuppressWarnings("deprecation")
	private String getRelease() {
		Date today = new Date(System.currentTimeMillis());

		logger.info("release: " + today.getMonth() + "." + ((today.getDay() - 1)/7+1));
		return today.getMonth() + "." + (today.getDay() - 1/7+1);
	}
	
}
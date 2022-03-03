package com.sentrydemos.springboot;

import java.sql.Date;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.Bean;

import org.springframework.boot.web.client.RestTemplateBuilder;
import org.springframework.web.client.RestTemplate;

import io.sentry.Sentry;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

//run with ./mvnw spring-boot:run in the spring-boot directory

@SpringBootApplication
public class Application {
	
	@Value("${SPRINGBOOT_LOCAL_ENV}")
	private String springbootlocalenv;
	
	@Value("${sentry.dsn}")
	private String sentryDSN; //value comes from the application.properties's sentry.dsn (value is also used with Logback)
	
	private static final Logger logger = LoggerFactory.getLogger(Application.class);
	
	public static void main(String[] args) {
		SpringApplication.run(Application.class, args);
	}

	@Bean
	RestTemplate restTemplate(RestTemplateBuilder builder) {
		return builder.build();
	}

	@SuppressWarnings("deprecation")
	private String getRelease() {
		Date today = new Date(System.currentTimeMillis());

		logger.info("release: " + today.getMonth() + "." + ((today.getDay() - 1)/7+1));
		return today.getMonth() + "." + (today.getDay() - 1/7+1);
	}
	
}
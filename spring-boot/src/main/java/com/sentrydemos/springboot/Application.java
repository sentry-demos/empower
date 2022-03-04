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

import io.sentry.SentryOptions.TracesSamplerCallback;
import io.sentry.SamplingContext;
import io.sentry.CustomSamplingContext;
import org.springframework.stereotype.Component;
import javax.servlet.http.HttpServletRequest;

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
	RestTemplate restTemplate(RestTemplateBuilder builder) {
		return builder.build();
	}

	@Component
	class CustomTracesSamplerCallback implements TracesSamplerCallback {
	@Override
		public Double sample(SamplingContext context) {
			// logger.info("> testing...."); // works
			// logger.info("> context is", context); // is blank
			// logger.info("> context is", "test..."); // is blank
			
			CustomSamplingContext customSamplingContext = context.getCustomSamplingContext();
			if (customSamplingContext != null) {
				HttpServletRequest request = (HttpServletRequest) customSamplingContext.get("request");

				// trying to find what on the request indicates it's an OPTIONS request, because we want to filter those out
				Sentry.configureScope(scope -> {
					scope.setContexts("> customSamplingContext...", request);
				});
				
				// this header only appears on OPTIONS requests, so could filter out OPTIONS this way
				// but it is not logging a value here, though is visible on the transaction event in Sentry.io
				// logger.info("> Access-Control-Request-Method...", request.getHeader("Access-Control-Request-Method"));
				return 1.0;
			} else {
				return 1.0;
			}
		}
	}
}

// Sentry.init...
// context -> {
// 	//context.getTransactionContext().getName() returns String: GET /products
// 	if (context.getTransactionContext().getOperation().equals("http.server") &&
// 		context.getTransactionContext().getName().startsWith("OPTIONS")) {
// 	  //Not sampling OPTIONS transactions
// 	  return 0.0;
// 	} else {
// 	  return 1.0;
// 	}
//   });
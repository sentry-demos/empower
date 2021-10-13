package com.sentrydemos.springboot;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.autoconfigure.EnableAutoConfiguration;
import org.springframework.boot.autoconfigure.jdbc.DataSourceAutoConfiguration;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.PropertySource;
import org.springframework.core.env.Environment;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.jdbc.datasource.SimpleDriverDataSource;
import org.springframework.util.ClassUtils;

import com.zaxxer.hikari.HikariConfig;
import com.zaxxer.hikari.HikariDataSource;

import java.lang.reflect.InvocationTargetException;

import javax.sql.DataSource;

import org.postgresql.Driver;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

@Configuration
public class AppConfig {

	private final Logger logger = LoggerFactory.getLogger(Application.class);

	
	/*
	@Value("${HOST}")
	private String host;
	
	@Value("${DATABASE}")
	private String database;
	
	@Value("${USERNAME}")
	private String username;
	
	@Value("${PASSWORD}")
	private String password;
	
	@Value("${CLOUD_SQL_CONNECTION_NAME}")
	private String cloudsqlconnectionname;
	
	@Bean
	public DataSource dataSource()
			throws InstantiationException, IllegalAccessException, IllegalArgumentException, InvocationTargetException {

		logger.info("initializing dataSource and jdbcTemplate...");
		
		
		String driverClassName = "org.postgresql.Driver";
		String jdbcUrl = "jdbc:postgresql://" + host + ":5432/" + database;

		final Class<?> driverClass = ClassUtils.resolveClassName(driverClassName, this.getClass().getClassLoader());
		final Driver driver = (Driver) ClassUtils.getConstructorIfAvailable(driverClass).newInstance();
		final DataSource dataSource = new SimpleDriverDataSource(driver, jdbcUrl, username, password);
		
		HikariConfig config = new HikariConfig();
		config.setJdbcUrl(String.format("jdbc:postgresql:///%s", database));
		config.setUsername(username);
		config.setPassword(password);

		config.addDataSourceProperty("socketFactory", "com.google.cloud.sql.postgres.SocketFactory");
		config.addDataSourceProperty("cloudSqlInstance", cloudsqlconnectionname);

		config.addDataSourceProperty("ipTypes", "PUBLIC,PRIVATE");

		DataSource dataSource = new HikariDataSource(config);
		
		return dataSource;

	}

	@Bean
	public JdbcTemplate jdbcTemplate()
			throws InstantiationException, IllegalAccessException, IllegalArgumentException, InvocationTargetException {
		JdbcTemplate jdbcTemplate = new JdbcTemplate(this.dataSource());
		return jdbcTemplate;
	}*/


}
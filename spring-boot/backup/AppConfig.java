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
import java.util.Properties;

import javax.sql.DataSource;

import org.postgresql.Driver;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

@Configuration
public class AppConfig {

	private final Logger logger = LoggerFactory.getLogger(Application.class);
	
	//@Value("${spring.cloud.gcp.sql.database-name}")
	@Value("${SPRINGBOOT_DATASOURCE_DB_NAME}")
	private String database;
	
	//@Value("${spring.datasource.username}")
	@Value("${SPRINGBOOT_DATASOURCE_USERNAME}")
	private String username;
	
	//@Value("${spring.datasource.password}")
	@Value("${SPRINGBOOT_DATASOURCE_PASSWORD}")
	private String password;
	
	//@Value("${spring.cloud.gcp.sql.instance-connection-name}")
	@Value("${SPRINGBOOT_DATASOURCE_GCP_CONNECTION_NAME}")
	private String cloudsqlconnectionname;
	
	//@Value("${spring.datasource.url}")
	@Value("${SPRINGBOOT_DATASOURCE_URL}")
	private String url;
	
	@Value("${SPRINGBOOT_LOCAL_ENV}")
	private String springbootlocalenv;

	@Bean
	public DataSource dataSource()
			throws InstantiationException, IllegalAccessException, IllegalArgumentException, InvocationTargetException {

		logger.info("initializing dataSource and jdbcTemplate...");
		
		String driverClassName = "org.postgresql.Driver";

		final Class<?> driverClass = ClassUtils.resolveClassName(driverClassName, this.getClass().getClassLoader());
		final Driver driver = (Driver) ClassUtils.getConstructorIfAvailable(driverClass).newInstance();
		//final DataSource dataSource = new SimpleDriverDataSource(driver, jdbcUrl, username, password);
		
		HikariConfig config = new HikariConfig();
		//config.setJdbcUrl(String.format("jdbc:postgresql:///%s", database));
		
		if (System.getenv("SPRINGBOOT_ENV") == null) {
			logger.info("SZ: dataSource");
			logger.info("Using test DB connection method with environment=" + springbootlocalenv);
			config.setUsername(username);
			logger.info("SZ2: dataSource");
			config.setPassword(password);
			logger.info("SZ3: dataSource");
			config.setJdbcUrl(url);
		} else {
			logger.info("Using production GCP connection method");
			
			logger.info("SZ: dataSource");
			config.setJdbcUrl(String.format("jdbc:postgresql:///%s", database));
			logger.info("jdbc " + String.format("jdbc:postgresql:///%s", database));
			config.setUsername(username);
			logger.info("username " + username);
			config.setPassword(password);
			config.addDataSourceProperty("socketFactory", "com.google.cloud.sql.postgres.SocketFactory");
			config.addDataSourceProperty("cloudSqlInstance", cloudsqlconnectionname);
			logger.info("cloudSqlInstance " + cloudsqlconnectionname);
			config.addDataSourceProperty("ipTypes", "PUBLIC,PRIVATE");
			
			
			/*logger.info("SZA: dataSource");
			String jdbcURL = String.format("jdbc:postgresql:///%s", database);
			logger.info("SZB: dataSource");
			Properties connProps = new Properties();
			logger.info("SZC: dataSource");
			connProps.setProperty("user", username);
			logger.info("SZD: dataSource");
		    connProps.setProperty("password", password);
		    logger.info("SZE: dataSource");
		    connProps.setProperty("sslmode", "disable");
		    logger.info("SZF: dataSource");
		    connProps.setProperty("socketFactory", "com.google.cloud.sql.postgres.SocketFactory");
		    logger.info("SZG: dataSource");
		    connProps.setProperty("cloudSqlInstance", cloudsqlconnectionname);
		    logger.info("SZH: dataSource");
		    connProps.setProperty("enableIamAuth", "true");
		    logger.info("SZI: dataSource");
		    
		    config.setJdbcUrl(jdbcURL);
		    logger.info("SZI: dataSource");
		    config.setDataSourceProperties(connProps);
		    logger.info("SZJ: dataSource");
		    config.setConnectionTimeout(10000);
		    logger.info("SZK: dataSource");*/
			
		}
		
		DataSource dataSource = new HikariDataSource(config);
		
		return dataSource;

	}

	@Bean
	public JdbcTemplate jdbcTemplate()
			throws InstantiationException, IllegalAccessException, IllegalArgumentException, InvocationTargetException {
		logger.info("SZ1: jdbcTemplate");
		JdbcTemplate jdbcTemplate = new JdbcTemplate(this.dataSource());
		logger.info("SZ2: jdbcTemplate");
		return jdbcTemplate;
	}

}
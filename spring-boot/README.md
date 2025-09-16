# SPRING BOOT
Extension to the Empower Plant UI/UX. This project was originally bootstrapped with [Create React App](https://github.com/facebook/create-react-app); this Java Spring Boot backend is available with the query param &backend=springboot, [e.g.] (http://localhost:3000/?se=simon&backend=springboot).

## Setup
This uses Java version 21 and Spring Boot version 3.5.3 [spring-boot-starter-parent](https://mvnrepository.com/artifact/org.springframework.boot/spring-boot-starter-parent/3.5.3)

2. Set env-config/*.env with
```
REACT_APP_BACKEND_URL_SPRINGBOOT=<value>
```

3. Set other `spring-boot/src/main/resources/application.properties` property values

4. Follow steps as described in `application.properties` for **Local DEV deployment** XOR **Cloud GCP deployment**

5. Put your DSN key in application.properties

### Run
Verify that the **DEV** section is not commented out in application.properties and values are set. The **GCP** section should be commented out.
```
spring.datasource.url=jdbc:postgresql://<server>:<port>/<database name>
server.port=8090
spring.cloud.gcp.sql.enabled=false
```

Run `./run.sh`

### Cloud GCP Deployment
Verify that the **GCP** section is not commented AND **DEV** section is commented (i.e. `application.properties` should have no values for `spring.datasource.url` nor `server.port`).
```
spring.cloud.gcp.sql.enabled=true
``` 

and to deploy
```
mvn clean package appengine:deploy
```

If you get invalid authentication credentials, try running first before deploying:
```
gcloud auth login
```

## Configuration Files
All configurations are in `src/main/resources/application.properties` and `src/main/appengine/app.yaml`.

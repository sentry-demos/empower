# SPRING BOOT
Extension to the Empower Plant UI/UX. This project was originally bootstrapped with [Create React App](https://github.com/facebook/create-react-app); this Java Spring Boot backend is available with the query param &backend=springboot, [e.g.] (http://localhost:5000/?se=simon&backend=springboot).

## Setup
This uses java version 8.

1. Verify that port 8090 is set for springboot in `react/src/utils/backendrouter.js`, 
```
  "springboot": {
      "test": "http://localhost:8090",
      "production": process.env.SPRINGBOOT_BACKEND
  }
```

2. Set react/.env with
```
REACT_APP_SPRINGBOOT_BACKEND=<value>
```

3. Set other `spring-boot/src/main/resources/application.properties` property values

4. Follow steps as described in `application.properties` for **Local DEV deployment** XOR **Cloud GCP deployment**

5. Put your DSN key in application.properties

### Local DEV deployment
Verify that the **DEV** section is not commented out in application.properties and values are set. The **GCP** section should be commented out.
```
spring.datasource.url=jdbc:postgresql://<server>:<port>/<database name>
server.port=8090
spring.cloud.gcp.sql.enabled=false
```

Run from terminal with `./mvnw spring-boot:run` from the spring-boot directory

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
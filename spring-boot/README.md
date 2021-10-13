#SPRING BOOT
Extension to the Empower Plant UI/UX. This project was originally bootstrapped with [Create React App](https://github.com/facebook/create-react-app); this Java Spring Boot backend is available with the query param &backend=springboot, [e.g.] (http://localhost:5000/?se=simon&backend=springboot).

## Setup
1. Update spring-boot/src/main/resources/application.properties to use 
```
server.port=8090
```
Verify that port http://localhost:8090 is set for springboot in react/src/utils/backendrouter.js, 
```
  "springboot": {
      "test": "http://localhost:8090",
      "production": process.env.SPRINGBOOT_BACKEND
  }
```

2. Verify other spring-boot/src/main/resources/application.properties property values are probably configured

## Run
1. Run from terminal with 
'''
./mvnw spring-boot:run
'''
from the spring-boot directory

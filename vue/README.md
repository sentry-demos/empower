# Vue Demo
This project was created using Vue CLI - https://cli.vuejs.org/guide/creating-a-project.html#vue-create
- Error Monitoring...Performance Monitoring...Release Health...
- BrowserTracing (Performance)  

## Setup
works with node v16.15.1

you may need to `npm install -g serve`

Note: This project sets the release details automatically using a combination of PACKAGE and releases (automatically computed)
Create a .env and enter following fields. See .env.example for an example:
1. VITE_APP_DSN
2. VITE_APP_PACKAGE

Edit the following fields within the run.sh file:
1. PACKAGE
2. SENTRY_ORG
3. SENTRY_PROJECT

## Run
npm install - this will install all dependencies  
./run.sh - this will build the files and will also serve the built file. This will also handle uploading of sourcemaps

## Demo
1. Home page
This page is slowed down using back end configurations, performance drops can be viewed under the 'home' transaction.
Selecting checkout will generate an Internal Server Error

2. About Us page
This page is slowed down using front end configurations, performance drops can be viewed under the 'about' transaction.

3. Subscribe page
Entering a valid email address will throw an error

4. Manually Trigger Errors page
This page allows you to generate errors by triggering them using buttons

## Deploy

```
gcloud auth login
./deploy.sh
```
app.yaml https://cloud.google.com/appengine/docs/standard/nodejs/config/appref


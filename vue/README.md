# Vue Demo
This project was created using Vue CLI - https://cli.vuejs.org/guide/creating-a-project.html#vue-create

## Features

### Frontend Monitoring
This Vue application includes comprehensive frontend monitoring capabilities through Sentry integration. The app automatically captures tracing data, performance profiles, error logs, session replays, and session health metrics. Browser profiling is enabled to provide detailed performance insights, and all relevant auto-instrumentation is configured by default. The system tracks suspect commits to correlate errors with specific code changes over time.

### Backend Routing System
The application features a dynamic backend routing system that automatically detects and routes to different backend services based on URL parameters. Users can specify backend types (e.g., ?backend=flask) to switch between Flask, Express, Spring Boot, ASP.NET Core, Laravel, Ruby, and Ruby on Rails services. Backend URLs are configured through environment variables and made globally accessible via window.BACKEND_URL for consistent backend communication across components.

### Experiment & Tag Tracking
Built-in experiment tracking includes SE tag tracking for sales engineering workflows, randomized customer type assignment (medium-plan, large-plan, small-plan, enterprise), and CEXP experiment tracking with conditional logic. The system provides frontend slowdown experiment controls, API type switching between different endpoints (e.g., products vs. products-join), and rage click detection with user feedback collection. User emails are automatically tracked and integrated with Sentry user context for enhanced error correlation.

### Infrastructure Configuration
The development environment includes Vite dev server headers configured for development profiling, while production deployments use App Engine headers for production profiling. Environment variable validation and templates ensure consistent configuration across different deployment environments. Utility functions provide components with easy access to experiment flags and configuration values.

- Error Monitoring...Performance Monitoring...Release Health...
- BrowserTracing (Performance)  

## Setup
works with node v16.15.1

you may need to `npm install -g serve`

Create a env-config/*.env and enter following fields. See env-config/example.env for an example:
```
VITE_APP_DSN
```

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


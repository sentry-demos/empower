# sentry-demos/laravel

Moved from old repository: https://github.com/sentry-demos/laravel

## Overview
To show how Sentry works in an example web app that uses PHP Laravel

Demonstrates:
- Import/integrate SDK into project
- Configuration
- Releases/Commits
- Event management

**Official Sentry documentation** found here:
https://docs.sentry.io/platforms/php/laravel/

Trigger an error that gets sent as Event to Sentry.io Platform
web.php has multiple endpoints for showing different ways that errors are handled

## Setup
#### Versions

| dependency      | version           
| ------------- |:-------------:| 
| sentry-laravel   | 2.2.0    |
| sentry-cli   | 1.53.0    |
| laravel | 8.0      |
| php   | 7.2.5     |

## First-time Setup
1. `composer install`
2. Set your DSN key, projectID, and Sentry OrganizationID in `.env`
3. make
4. `http://localhost:8000/handled` and `http://localhost:8000/unhandled` to trigger errors

# Run With Docker
1. docker build -t my-first-image .
2. docker run -p 8000:8000 my-first-image

# GCP Cloud Run
1. make deploy_gcp

## Technical Notes or Troubleshooting
This demo leverages log channels to record more info and allow you
to configure the log level in `logging.php`.
The minimum event level is set to `debug` by default which may be
too verbose. 

# GIF

![Alt Text](overview.gif)

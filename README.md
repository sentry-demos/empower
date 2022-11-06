# Application Monitoring
Also called the Empower Plant UI/UX. This project was bootstrapped with [Create React App](https://github.com/facebook/create-react-app). Features the following...
- Error Monitoring...Performance Monitoring...Release Health...
- BrowserTracing (Performance)  
- Sentry.Profiler (class components)  
- Sentry.withSentryRouting(Route); (react-router)  
- FlaskIntegration, SqlAlchemyIntegration

| sentry    | version
| ------------- |:-------------:|
| @sentry/react | 6.16.1 |
| @sentry/tracing | 6.16.1 |
| sentry_sdk | 1.5.1 |
| @sentry/node | 6.16.1 |
| sentry-spring-boot-starter | 5.5.1 |
| sentry-logback | 5.5.1 |

## Setup
1. Permit your IP address in CloudSQL.
2. Copy `env-config/local.env` from the private fork, [application-monitoring-deploy](https://github.com/sentry-demos/application-monitoring-deploy/tree/master/env-config), or, if you don't have access to it, follow `env-config/example.env`.
4. The `REACT_APP_FLASK_BACKEND` in `env-config/*.env` points to the backend instance deployed to AppEngine, the same one used by the cloud-hosted React web app. Flask is the default backend. If you expect to run other backend types, add values for those in `env-config/*.env` as well (i.e. `REACT_APP_EXPRESS_BACKEND`).

`deploy.sh` takes a list of projects as arguments and will attempt to install dependencies, build and run or deploy them as long as each supplies a working `build.sh` and `run.sh` scripts. (Right now only React, Flask and Vue have been confirmed to work). For projects that don't
work feel free to read their README and submit a PR that makes it work. 

NOTE: `build.sh` and `run.sh` files in each project are not meant to be run direclty, use top-level `deploy.sh` instead because it sets all required environment variables.

If you run locally and only deploy `react` it will automatically point to `staging` backends, however if you include a backend
projects in the command `react` will magically point to it instead of staging (still requires `&be=<backend>` url param).

`deploy.sh` takes another argument `--env=<env>`, which can be either `local`, `staging` or `production`. Each value corresponds to a file in `env-config` directory. `local` is a special value, most significantly it will run all webservers locally instead of deploying to Google App Engine.

`deploy.sh` does everything including validating that all required values are set in the `env-config/*.env`, that each project's
DSN and project name point to the same project, and that you are not accidentally deploying to production, etc.

For more info See the [comment at the top of `deploy.sh` file](https://github.com/sentry-demos/application-monitoring/blob/master/deploy.sh#L3-L47).

## Run

Pick one of two ways to run the React app:

### 1) Run React app w/ sourcemaps, suspect commits
Recommended to use this command rather than `npm start`, as deploy.sh uploads source maps and handles crashes more realistically.
```
./deploy.sh --env=local react flask
```
or
```
./deploy.sh react --env=local
```

### 2) Run React app w/ hot reload
NOTE: this will cause crashing errors to be tagged in sentry as handled (`handled: true`)
```
cd react
../env.sh local npm start
```

## Trigger an error

Add +2 quantity of a single item to Cart and purchase in order to trigger an Error. Visit the routes defined in src/index.js to produce transactions.

## Deploy to Prod
This script deploys the flagship apps React + Flask. For deploying a single app to App Engine, check each platform's README for specific instructions. Make sure you don't have any local changes to `env-config/production.env`.
```
./deploy.sh react --env=production
```
You can put all 4 apps in deploy.sh for deployment, but that's 4 apps you could be taking down at once, which other people are relying on. With great power, comes great responsibility.  

Run `gcloud auth login` if it asks you to authenticate, or insert YubiKey.  

## Deploy to Staging
```
./deploy.sh react flask vue --env=staging
```

## Updating The Apps
```
## Check if you're on your fork. If so, you should see:
git remote -v
origin	git@github.com:<your_handle>/application-monitoring.git (fetch)
origin	git@github.com:<your_handle>/application-monitoring.git (push)
upstream	git@github.com:sentry-demos/application-monitoring.git (fetch)
upstream	git@github.com:sentry-demos/application-monitoring.git (push)

# If you don't have an upstream
git remote add upstream git@github.com:sentry-demos/application-monitoring.git

# Make sure you're on master
git checkout master

# get updates from the upstream
git fetch upstream master
git merge upstream/master

# merge those updates into your current branch, if it's behind
git checkout yourbranch
git merge master

# update sentry_sdk's and other modules
cd react && rm -rf node_modules && npm install
cd flask && source env/bin/activate && pip install -r requirements.txt

# Check that your react/.env, flask/.env and deploy.sh still have correct values
```

## Troubleshooting
See [troubleshooting](./troubleshooting.md)

## Gcloud
```
gcloud app versions list
gcloud app deploy
gcloud app browse
gcloud app services list
gcloud app logs tail -s application-monitoring-react
gcloud app logs tail -s application-monitoring-flask
gcloud --help
gcloud topic configurations
gcloud auth
gcloud auth application-default
gcloud auth login
gcloud auth list
gcloud config set account `ACCOUNT`
gcloud config list, to display current account
```
`gcloud app deploy` does not support `--update-env-vars RELEASE=$RELEASE` like `gcloud run deploy` does with Cloud Run

## Versions

| non-sentry    | version
| ------------- |:-------------:|
| npx | 7.8.0 |
| npm | 7.8.0 |
| node | v.14.2.0 |
| python | 3 |
| react | ^17.0.2 |
| react-dom | ^17.0.2 |
| react-router-dom | ^5.2.0 |
| react-scripts | 4.0.3 |


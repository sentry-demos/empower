# Application Monitoring
Also called the Empower Plant UI/UX. This project was bootstrapped with [Create React App](https://github.com/facebook/create-react-app). Features the following...
- Error Monitoring...Performance Monitoring...Release Health...
- BrowserTracing (Performance)  
- Sentry.Profiler (class components)  
- Sentry.withSentryRouting(Route); (react-router)  
- FlaskIntegration, SqlAlchemyIntegration

| sentry    | version
| ------------- |:-------------:|
| @sentry/react | 6.12.0-beta.2 |
| @sentry/tracing | 6.12.0-beta.2 |
| sentry_sdk | 1.3.1 |

## Setup
1. Permit your IP address in CloudSQL.
2. Create a react/.env and enter your DSN. See .env.example for an example.
3. Create a flask/.env and enter your DSN. See .env.example for an example. Ask a colleague for the values.
4. The REACT_APP_BACKEND in react/.env represents Flask in AppEngine, this is used when you access the prod React web app.

```
# React
npm install

# Flask
cd flask
python3 -m venv env
source env/bin/activate
pip install -r requirements.txt
```

## Run
```
cd react
## or
cd flask
```

and

```
# React w/ sourcemaps, suspect commits
./run.sh

# React w/ hot reload
npm start

# Flask
source env/bin/activate
./run.sh
```

Add +2 quantity of a single item to Cart and purchase in order to trigger an Error. Visit all routes defined in src/index.js to produce transactions for them.


## Deploy
This run script deploys React + Flask. See the run script for individual gcloud commands you could use for any of the backends /node /ruby etc.
```
./run.sh
```

## Troubleshooting
### Upgrading
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

# update sentry_sdk's and other modules
cd react && npm install
cd flask && pip install -r requirements.txt

# Check that your react/.env, flask/.env and deploy.sh still have correct values
```
### Releases
Q. `--update-env-vars` is not available for `gcloud app deploy`, therefore can't pass a RELEASE upon deploying. Luckily it's already built into the /build which gets uploaded, and sentry-cli generated it, as well as the RELEASE that sentry-cli uses for uploading source maps.

A. So, creating the dynamic Release inside of main.py. Hard-coding it into .env wouldn't help, as it needs to be dynamic. This release may not match what sentry-cli is generating for release (due to clock skew), but we're not uploading source maps for python. Worst case, the Python release is slightly different than the React release, but this shouldn't matter, because two separate apps (repo) typically have unique app version numbers anyways (you version them separately).

### Gcloud commands
```
gcloud app versions list
gcloud app deploy
gcloud app browse
gcloud app services list
gcloud app logs tail -s application-monitoring-react
gcloud app logs tail -s application-monitoring-flask
```

### Other
Don't use a sqlalchemy or pg8000 that is higher than sqlalchemy==1.3.15, pg8000==1.12.5, or else database won't work.

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

'default' is a function applied to objects that aren't serializable.  
use 'default' or else you get "Object of type datetime is not JSON serializable":  
json.dumps(results, default=str)  

`gcloud app deploy` does not support `--update-env-vars RELEASE=$RELEASE` like `gcloud run deploy` does with Cloud Run

https://dev.to/brad_beggs/handling-react-form-submit-with-redirect-async-await-for-the-beyond-beginner-57of

https://www.pluralsight.com/guides/how-to-transition-to-another-route-on-successful-async-redux-action

https://reactjs.org/docs/forms.html

State Hooks vs Effect Hooks vs Context
https://reactjs.org/docs/hooks-state.html

Context
https://reactjs.org/docs/hooks-effect.html

https://docs.sentry.io/platforms/python/guides/flask/configuration/filtering/#using-sampling-to-filter-transaction-events

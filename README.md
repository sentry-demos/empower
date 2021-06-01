# Application Monitoring
## Empower Plant

This project was bootstrapped with [Create React App](https://github.com/facebook/create-react-app).

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

don't use versions any higher than:  
```
sqlalchemy==1.3.15
pg8000==1.12.5
```
or else db won't work

redux, react-redux, redux-logger, will do later.

| sentry    | version
| ------------- |:-------------:|
| @sentry/react | ^6.2.5 |
| @sentry/tracing | ^6.2.5 |
| sentry_sdk | 1.1.0 |

#### Sentry Integrations
BrowserTracing (Performance)  
Sentry.Profiler (class components)  
Sentry.withSentryRouting(Route); (react-router)  
FlaskIntegration, SqlAlchemyIntegration


## Setup
```
npm install
```

cd flask && python3 -m venv env
source env/bin/activate
pip install -r requirements.txt

## Run
Dev
```
npm start
```

```
cd flask && ./run.sh
#python3 main.py
```

Prod
```
npm build
serve -s build
```

Prod
```
# React
npm run build && gcloud app deploy --version=<version>

# Flask
cd flask && gcloud app deploy
```

--update-env-vars is not available for `gcloud app deploy`, so creating the dynamic Release inside of main.py. Hard-coding it into .env wouldn't help (as it needs to be dynamic)

two different apps are usually not the same app version, but we're choosing so with Calendar versioning.

TODO add .png to react's `app.yaml` here: (json|ico|js)$ so don't get, "Error while trying to use the following icon from the Manifest: https://empower-plant-content-1-dot-sales-engineering-sf.appspot.com/logo192.png (Download error or resource isn't a valid image)"

## gcloud
gcloud app versions list
gcloud app deploy
gcloud app browse
gcloud app services list
gcloud app logs tail -s empower-plant-content-1
gcloud app logs tail -s application-monitoring-flask

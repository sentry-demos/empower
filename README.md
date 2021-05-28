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
python3 main.py
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


## gcloud
gcloud app versions list
gcloud app deploy
gcloud app browse
gcloud app services list
gcloud app logs tail -s empower-plant-content-1
gcloud app logs tail -s application-monitoring-flask

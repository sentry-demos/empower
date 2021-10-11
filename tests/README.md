# Test Data Automation
Runs automted tests against Sentry demos on GCP, in order to generate errors and transactions to be sent to Sentry.io.

## Components / Moving parts
- `conftest.py` -> Sauce Labs configuration (browsers) for frontend_tests
- `backend_tests/backend_test.py` -> Hits /handled, /unhandled/, + /checkout backend demo APIs

# Tests

## Setup
```
python3 -m venv venv
source env/bin/activate
pip install -r requirements.txt
```

Update your endpoint (URL) in `endpoints.yaml` -> (http://application-monitoring-react-dot-sales-engineering-sf.appspot.com/ <-- '/' at end)

Saucelabs Authentication
```
export SAUCE_USERNAME=<>
export SAUCE_ACCESS_KEY=<>
```

```
chmod u+x tests/script.sh
```

## FrontEnd / Selenium (`desktop_web` directory)
Pulls up Sentry frontend in various browsers in parallel via selenium scripts.
Test case will add items to cart and then click checkout

```
py.test -s -n 4 desktop_web
```

`-n` is for number of threads

# To run "continuously" in VM
Use an isolated VM since it's constantly occupying +2 threads simultaneously
```
source .virtualenv/bin/activate
nohup ./script.sh &
```

How to stop it
```
ps fjx
kill -9 <PID of the script.sh>
```

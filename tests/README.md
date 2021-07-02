# Test Data Automation
Runs automted tests against Sentry demos on GCP, in order to generate errors and transactions to be sent to Sentry.io

## Components / Moving parts
- `create_job.sh` -> creates GCP cron job which hits Travis requests APIs to trigger build
- `.travis.yml` -> runs automated tests / simulations
- `conftest.py` -> Sauce Labs configuration (browsers) for frontend_tests
- `backend_tests/backend_test.py` -> Hits /handled, /unhandled/, + /checkout backend demo APIs

create_cron_job.sh -> GCP-cron job (runs every 20 min from midnight-6am) -> TravisCI (runs tests)

# Tests

## Setup
```
python3 -m venv env
source env/bin/activate
pip install -r requirements.txt
```

Update your endpoint (URL) in `endpoints.yaml`  
http://application-monitoring-react-dot-sales-engineering-sf.appspot.com/ <-- '/' at end?  
http://localhost:5000/  

## FrontEnd / Selenium (`frontend_tests` directory)
Pulls up Sentry frontend in various browsers in parallel via selenium scripts.
Test case will add items to cart and then click checkout

```
py.test -s -n 2 frontend_tests
```

`-n` is for number of threads


# Additional Setup instructions/context
### Python2

SAUCE_USERNAME + SAUCE_ACCESS_KEY environment variables
See https://www.notion.so/sentry/Test-Data-Automation-Performance-Web-Vitals-Trends-edbe8d54b46f4bd987fa2ca487593ea9#7e633c0acab3430cb11aaa775e9bae89

If you get this error during pip install: `ERROR: Package 'setuptools' requires a different Python: 2.7.12 not in '>=3.5'` then run:
```
pip install -U pip
pip install setuptools==44.0.0

# and re-rerun:
pip install -r requirements.txt
```
# Setup: Setting up cron job to trigger simulations

We can trigger the travis builds on a schedule via Google Cloud Scheduler cron jobs.

To register:
```
./create_cron_job.sh
```

Docs:
- https://cloud.google.com/sdk/gcloud/reference/scheduler/jobs/create/
- https://docs.travis-ci.com/user/triggering-builds/

Sentry docs:
- https://docs.sentry.io/performance/distributed-tracing/
- https://docs.sentry.io/performance/performance-metrics/

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


## Todo
Why are OPTIONS http.method transactions surfacing for the AppEngine instance?  
This doesn't happen when hitting localhost:5000/products
TRY accessing application-monitoring.com/products manually, see if it happens


The average `i` should be 10?  
for i in range(random.randrange(20))
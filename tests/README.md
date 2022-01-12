# Test Data Automation
Runs automted tests against Sentry demos on GCP, in order to generate errors and transactions to be sent to Sentry.io.

## Components / Moving parts
- `conftest.py` -> Sauce Labs configuration (browsers) for frontend_tests
- `backend_tests/backend_test.py` -> Hits /handled, /unhandled/, + /checkout backend demo APIs
- Selectors for button elements in the React Native app can be found via connecting an Appium Inspector to your Saucelabs instance.
- [SauceLabs Inspector](https://github.com/appium/appium-inspector) download and launch this Desktop program, get the JSON config from someone.

# Tests

## Setup
```
python3 -m venv env
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

Make a .env and put DSN in there if you want catch errors for the pytests failing (not the Apps themselves having errors)

## FrontEnd / Selenium (`desktop_web` directory)
Pulls up Sentry frontend in various browsers in parallel via selenium scripts.
Test case will add items to cart and then click checkout

```
py.test -s -n 4 desktop_web
```

`-n` is for number of threads

How to run one test:
```
py.test -s -n 4 desktop_web/test_homepage.py
py.test -s -n 4 mobile_native/android_react_native/test_homescreen_react_native_android.py
```

# To run "continuously" in VM
Use an isolated VM since it's constantly occupying +2 threads simultaneously
```
source .virtualenv/bin/activate
nohup ./mobile_native.sh >/dev/null 2>&1 &
nohup ./desktop_web.sh >/dev/null 2>&1 &
```

How to stop it
```
ps fjx
kill -9 <PID of the script.sh>
```
# Troubleshooting

### SSL Cert Issues

Problem: When locally running TDA tests, i.e. `py.test -s -n 4 desktop_web`, if you experience this error (or similar relating to SSL Cert):

```
E           urllib3.exceptions.MaxRetryError: HTTPSConnectionPool(host='ondemand.us-west-1.saucelabs.com', port=443): Max retries exceeded with url: /wd/hub/session (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: self signed certificate in certificate chain (_ssl.c:1091)')))

venv/lib/python3.7/site-packages/urllib3/util/retry.py:574: MaxRetryError
```

<details>
<summary>Click to toggle error screenshot</summary>

![Screen Shot 2021-11-29 at 2 57 11 PM](https://user-images.githubusercontent.com/12092849/145083651-5479f05c-107f-4d46-a981-1c728679172f.png)

</details>

**Solution:** A workaround is to locally change the `SAUCELABS_PROTOCOL` constant in `conftest.py` from `https` to `http`.

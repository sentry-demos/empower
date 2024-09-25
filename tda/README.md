Below is a bit out of date, please see 
https://github.com/sentry-demos/empower/pull/173

# Test Data Automation
Runs automted tests against Sentry demos on GCP, in order to generate errors and transactions to be sent to Sentry.io.


** Some of the doc below is out of date **

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
py.test -s -n 4 mobile_native/ios_react_native/test_uncaughtthrownerror_react_native_ios.py
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

### ssh: Could not resolve hostname empower-tda-and-crons-staging.us-central1-a.sales-engineering-sf: nodename nor servname provided, or not known

1. Test that `gcloud compute ssh empower-tda-and-crons` works
2. Run `gcloud compute config-ssh` to add any new instances to your `~/.ssh/config`

### TypeError: required field "lineno" missing from alias
```
  File "/Users/kosty/home/empower/tda/env/lib/python3.10/site-packages/_pytest/assertion/rewrite.py", line 360, in _rewrite_test
    co = compile(tree, fn_, "exec", dont_inherit=True)
TypeError: required field "lineno" missing from alias
```
You will need to downgrade your python version to fix this:
1. Install Python 3.10 with `brew install python@3.10` (macos) or google "install python 3.10 linux" for `apt-get` instructions for GCP VM.
2. Nuke your `venv`-created `env`: `deactivate && rm -rf env`
3. `pip3 install virtualenv` or `python3 -m pip install virtualenv`, etc.
4. Create a virtual environment that uses Python 3.10 instead of your global python `virtualenv --python="/opt/homebrew/Cellar/python@3.10/3.10.??/bin/python3.10" env` (exact path may differ, might be able to find it with `which python3.10` command)
5. The usual:
```
source env/bin/activate
pip install -r requirements.txt
```
6. Instead of using `py.test` or `pytest` executable that is probably global and points to your Python 3.10+ installation, use `python3 -m pytest` that will pick up the Python 3.10 from virtual environment. (Not an issue on GCP tda box)

Note that handled errors will not increment the crash counts in Release Health. But the Release Health UI does separate Handled from Unhandled Issues.

https://appium.io/docs/en/commands/device/app/launch-app/

Test names must begin with a prefix of `test_` or else they won't run.

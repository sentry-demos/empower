Below is a bit out of date, please see 
https://github.com/sentry-demos/empower/pull/173

# Test Data Automation
Runs automted tests against Sentry demos on GCP, in order to generate errors and transactions to be sent to Sentry.io.

## Components / Moving parts
- `conftest.py` -> Sauce Labs configuration (browsers) for frontend_tests
- Selectors for button elements in the React Native app can be found via connecting an Appium Inspector to your Saucelabs instance.
- [SauceLabs Inspector](https://github.com/appium/appium-inspector) download and launch this Desktop program, get the JSON config from someone.

# How to run locally to verify a new test works

Run just 1 test locally:
```
./deploy _tda --env=local -- ./run_local.sh desktop_web/test_ai_agent.py
```

Run entire suite locally:
```
./deploy _tda --env=local
```

# How to deploy to production

This will take care of everything
```
./deploy _tda --env=production
```

# Troubleshooting

### ssh: Could not resolve hostname empower-tda-and-crons-staging.us-central1-a.sales-engineering-sf: nodename nor servname provided, or not known

1. Test that `gcloud compute ssh empower-tda-and-crons` works
2. Run `gcloud compute config-ssh` to add any new instances to your `~/.ssh/config`

### TypeError: required field "lineno" missing from alias
```
  File "/Users/kosty/home/empower/_tda/env/lib/python3.10/site-packages/_pytest/assertion/rewrite.py", line 360, in _rewrite_test
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


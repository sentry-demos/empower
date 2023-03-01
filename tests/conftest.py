import pytest
from os import environ
import os
import release_version_manager as ReleaseVersion
import random
import subprocess
import urllib.parse
import atexit

from selenium import webdriver
from appium import webdriver as appiumdriver
from appium.options.android import UiAutomator2Options
from appium.options.ios import XCUITestOptions
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.remote.remote_connection import RemoteConnection
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.safari.options import Options as SafariOptions
from datetime import datetime, timedelta

import sentry_sdk
from dotenv import load_dotenv
load_dotenv()

def get_system_user():
    return subprocess.check_output(['id', '-un']).strip().decode()

# Get current timestamp, with +/- adjustment if desired, as string in ISO format (for Sentry URLs)
# round seconds down (floor): adjust_seconds = 0
# round seconds up (ceil): adjust_seconds = 1
def get_current_time_iso_utc(adjust_seconds=0):
    dt = datetime.utcnow().replace(microsecond=0) + timedelta(seconds = adjust_seconds)
    return dt.isoformat()


# Example command usage:
#
#   SE_TAG=tda-my-new-test BATCH_SIZE=10 py.test -n 6 desktop_web
#

start_time = get_current_time_iso_utc()

SAUCELABS_PROTOCOL = "https://"
DSN = "https://9802de20229e4afdaa0d60796cbb44d7@o87286.ingest.sentry.io/5390094"
ENVIRONMENT = os.getenv("ENVIRONMENT") or "production"
# SE_TAG will be both:
#
# 1. Passed on to desktop_web as ?se= URL parameter so will show up in
# application-monitoring-* project issues generated as a result of running the test
#
# 2. Used for internal reporting of this test automation's own errors (to DSN above,
# i.e. "job-monitor-application-monitoring" project)
#
# If no value is provided will attemptq

SE_TAG = os.getenv("SE_TAG") or get_system_user()

# BATCH_SIZE can be either <NUMBER> or random_<NUMBER>
# The later means each time a test is run the inner steps will be repeated a random
# number of times between 0 and <NUMBER> - 1
# e.g. BATCH_SIZE=5, or BATCH_SIZE=random_100
BATCH_SIZE = os.getenv("BATCH_SIZE") or "1"

BACKENDS = (os.getenv("BACKENDS") or "flask,express,springboot,ruby,laravel").split(',')

def pytest_configure():
    pytest.SE_TAG=SE_TAG

    if BATCH_SIZE.startswith("random_"):
        pytest.batch_size = lambda: random.randrange(int(BATCH_SIZE.split('_')[1]))
    else:
        pytest.batch_size = lambda: int(BATCH_SIZE)

    def random_backend(exclude=[]):
        exclude = [exclude] if isinstance(exclude, str) else exclude
        backends = list(set(BACKENDS) - set(exclude))
        return random.sample(backends, 1)[0]
    pytest.random_backend = random_backend

import urllib3
urllib3.disable_warnings()

sentry_sdk.init(
    dsn=DSN,
    traces_sample_rate=0,
    environment=ENVIRONMENT,
)

sentry_sdk.set_tag("se", SE_TAG)

_browser2class = {
    'chrome': ChromeOptions,
    'firefox': FirefoxOptions,
    'safari': SafariOptions
}

desktop_browsers = [
    {
        "platformName": "Windows 10",
        "browserName": "chrome",
        "browserVersion": "latest",
    }, {
        "platformName": "Windows 10",
        "browserName": "firefox",
        "browserVersion": "latest",
    }, {
        "platformName": "OS X 10.13",
        "browserName": "safari",
        "browserVersion": "latest-1",
    }, {
        "platformName": "OS X 10.13",
        "browserName": "chrome",
        "browserVersion": "latest",
    }]

def pytest_addoption(parser):
    parser.addoption("--dc", action="store", default='us', help="Set Sauce Labs Data Center (US or EU)")

@pytest.fixture
def data_center(request):
    return request.config.getoption('--dc')

@pytest.fixture(params=desktop_browsers)
def desktop_web_driver(request, data_center):

    try:
        sentry_sdk.set_tag("pytestPlatform", "desktop_web")

        test_name = request.node.name
        build_tag = environ.get('BUILD_TAG', "Application-Monitoring-TDA")

        username = environ['SAUCE_USERNAME']
        access_key = environ['SAUCE_ACCESS_KEY']

        if data_center and data_center.lower() == 'eu':
            selenium_endpoint = SAUCELABS_PROTOCOL + "{}:{}@ondemand.eu-central-1.saucelabs.com/wd/hub".format(username, access_key)
        else:
            selenium_endpoint = SAUCELABS_PROTOCOL + "{}:{}@ondemand.us-west-1.saucelabs.com/wd/hub".format(username, access_key)

        options = _browser2class[request.param['browserName']]()
        for c in ['platformName', 'browserVersion']:
            options.set_capability(c, request.param[c])
        options.set_capability('sauce:options', {
            'seleniumVersion': '4.8.0',
            'build': build_tag,
            'name': test_name
        })

        browser = webdriver.Remote(
            command_executor=selenium_endpoint,
            options=options,
            keep_alive=True
        )

        browser.implicitly_wait(10)

        sentry_sdk.set_tag("seleniumSessionId", browser.session_id)

        # This is specifically for SauceLabs plugin.
        # In case test fails after selenium session creation having this here will help track it down.
        if browser is not None:
            print("SauceOnDemandSessionID={} job-name={}".format(browser.session_id, test_name))
        else:
            raise WebDriverException("Never created!")

        yield browser

        # Teardown starts here
        # report results
        # use the test result to send the pass/fail status to Sauce Labs
        sauce_result = "failed" if request.node.rep_call.failed else "passed"

        # Handler failure scenario, send to Sentry job-monitor-application-monitoring
        if sauce_result == "failed":
            sentry_sdk.capture_message("Sauce Result: %s" % (sauce_result))

        browser.execute_script("sauce:job-result={}".format(sauce_result))
        browser.quit()

        # desktop_web tests finished, send to Sentry job-monitor-application-monitoring, look for tags pytestName, pytestPlatform, seleniumSessionId
        sentry_sdk.capture_message("Selenium Session Done")
    
    except Exception as err:
        sentry_sdk.capture_exception(err)

@pytest.fixture
def android_react_native_emu_driver(request, data_center):

    try:
        sentry_sdk.set_tag("pytestPlatform", "android_react_native")

        username_cap = environ['SAUCE_USERNAME']
        access_key_cap = environ['SAUCE_ACCESS_KEY']
        release_version = ReleaseVersion.latest_react_native_github_release()

        options = UiAutomator2Options().load_capabilities({
            'username': username_cap,
            'accessKey': access_key_cap,
            'deviceName': 'Android GoogleAPI Emulator',
            'platformVersion': '10.0',
            'platformName': 'Android',
            'app': f'https://github.com/sentry-demos/sentry_react_native/releases/download/{release_version}/app-release.apk',
            'sauce:options': {
                'appiumVersion': '1.20.2',
                'build': 'RDC-Android-Python-Best-Practice',
                'name': request.node.name
            },
            'appWaitForLaunch': False
        })

        if data_center and data_center.lower() == 'eu':
            sauce_url = SAUCELABS_PROTOCOL + "{}:{}@ondemand.eu-central-1.saucelabs.com/wd/hub".format(username_cap, access_key_cap)
        else:
            sauce_url = SAUCELABS_PROTOCOL + "{}:{}@ondemand.us-west-1.saucelabs.com/wd/hub".format(username_cap, access_key_cap)

        driver = appiumdriver.Remote(sauce_url, options=options)
        driver.implicitly_wait(20)

        sentry_sdk.set_tag("seleniumSessionId", driver.session_id)

        yield driver
        sauce_result = "failed" if request.node.rep_call.failed else "passed"
        driver.execute_script("sauce:job-result={}".format(sauce_result))
        driver.quit()

        # android_react_native tests finished, send to Sentry job-monitor-application-monitoring, look for tags pytestName, pytestPlatform, seleniumSessionId
        sentry_sdk.capture_message("Selenium Session Done")
    
    except Exception as err:
        sentry_sdk.capture_exception(err)

@pytest.fixture
def android_emu_driver(request, data_center):

    try:
        sentry_sdk.set_tag("pytestPlatform", "android")

        username_cap = environ['SAUCE_USERNAME']
        access_key_cap = environ['SAUCE_ACCESS_KEY']
        release_version = ReleaseVersion.latest_android_github_release()

        options = UiAutomator2Options().load_capabilities({
            'username': username_cap,
            'accessKey': access_key_cap,
            'deviceName': 'Android GoogleAPI Emulator',
            'platformVersion': '10.0',
            'platformName': 'Android',
            'app': f'https://github.com/sentry-demos/android/releases/download/{release_version}/app-release.apk',
            'sauce:options': {
                'appiumVersion': '1.20.2',
                'build': 'RDC-Android-Python-Best-Practice',
                'name': request.node.name
            },
            'appWaitForLaunch': False
        })

        if data_center and data_center.lower() == 'eu':
            sauce_url = SAUCELABS_PROTOCOL + "{}:{}@ondemand.eu-central-1.saucelabs.com/wd/hub".format(username_cap, access_key_cap)
        else:
            sauce_url = SAUCELABS_PROTOCOL + "{}:{}@ondemand.us-west-1.saucelabs.com/wd/hub".format(username_cap, access_key_cap)

        driver = appiumdriver.Remote(sauce_url, options=options)
        driver.implicitly_wait(20)

        sentry_sdk.set_tag("seleniumSessionId", driver.session_id)

        yield driver
        sauce_result = "failed" if request.node.rep_call.failed else "passed"
        driver.execute_script("sauce:job-result={}".format(sauce_result))
        driver.quit()

        # android tests finished, send to Sentry job-monitor-application-monitoring, look for tags pytestName, pytestPlatform, seleniumSessionId
        sentry_sdk.capture_message("Selenium Session Done")

    except Exception as err:
        sentry_sdk.capture_exception(err)

@pytest.fixture
def ios_react_native_sim_driver(request, data_center):

    try:
        sentry_sdk.set_tag("pytestPlatform", "ios_react_native")

        username_cap = environ['SAUCE_USERNAME']
        access_key_cap = environ['SAUCE_ACCESS_KEY']
        release_version = ReleaseVersion.latest_react_native_github_release()

        options = XCUITestOptions().load_capabilities({
            'username': username_cap,
            'accessKey': access_key_cap,
            'appium:deviceName': 'iPhone 11 Simulator',
            'platformName': 'iOS',
            'appium:platformVersion': '14.5',

            'sauce:options': {
                'appiumVersion': '1.21.0',
                'build': 'RDC-iOS-Python-Best-Practice',
                'name': request.node.name,
            },
            'appium:app': f'https://github.com/sentry-demos/sentry_react_native/releases/download/{release_version}/sentry_react_native.app.zip',
        })

        if data_center and data_center.lower() == 'eu':
            sauce_url = SAUCELABS_PROTOCOL + "{}:{}@ondemand.eu-central-1.saucelabs.com/wd/hub".format(username_cap, access_key_cap)
        else:
            sauce_url = SAUCELABS_PROTOCOL + "{}:{}@ondemand.us-west-1.saucelabs.com/wd/hub".format(username_cap, access_key_cap)

        driver = appiumdriver.Remote(sauce_url, options=options)
        driver.implicitly_wait(20)

        sentry_sdk.set_tag("seleniumSessionId", driver.session_id)

        yield driver
        sauce_result = "failed" if request.node.rep_call.failed else "passed"
        driver.execute_script("sauce:job-result={}".format(sauce_result))
        driver.quit()

        # ios_react_native tests finished, send to Sentry job-monitor-application-monitoring, look for tags pytestName, pytestPlatform, seleniumSessionId
        sentry_sdk.capture_message("Selenium Session Done")
    
    except Exception as err:
        sentry_sdk.capture_exception(err)

@pytest.fixture
def ios_sim_driver(request, data_center):

    try:
        sentry_sdk.set_tag("pytestPlatform", "ios")

        username_cap = environ['SAUCE_USERNAME']
        access_key_cap = environ['SAUCE_ACCESS_KEY']
        release_version = ReleaseVersion.latest_ios_github_release()

        options = XCUITestOptions().load_capabilities({
            'username': username_cap,
            'accessKey': access_key_cap,
            'appium:deviceName': 'iPhone 11 Simulator',
            'platformName': 'iOS',
            'appium:platformVersion': '14.5',

            'sauce:options': {
                'appiumVersion': '1.21.0',
                'build': 'RDC-iOS-Mobile-Native',
                'name': request.node.name,
            },
            'appium:app': f'https://github.com/sentry-demos/ios/releases/download/{release_version}/EmpowerPlant_release.zip',
        })

        if data_center and data_center.lower() == 'eu':
            sauce_url = SAUCELABS_PROTOCOL + "{}:{}@ondemand.eu-central-1.saucelabs.com/wd/hub".format(username_cap, access_key_cap)
        else:
            sauce_url = SAUCELABS_PROTOCOL + "{}:{}@ondemand.us-west-1.saucelabs.com/wd/hub".format(username_cap, access_key_cap)

        driver = appiumdriver.Remote(sauce_url, options=options)
        driver.implicitly_wait(20)

        sentry_sdk.set_tag("seleniumSessionId", driver.session_id)

        yield driver
        sauce_result = "failed" if request.node.rep_call.failed else "passed"
        driver.execute_script("sauce:job-result={}".format(sauce_result))
        driver.quit()

        # ios tests finished, send to Sentry job-monitor-application-monitoring, look for tags pytestName, pytestPlatform, seleniumSessionId
        sentry_sdk.capture_message("Selenium Session Done")
        
    except Exception as err:
        sentry_sdk.capture_exception(err)


@pytest.hookimpl(hookwrapper=True, tryfirst=True)
def pytest_runtest_makereport(item, call):
    # this sets the result as a test attribute for Sauce Labs reporting.
    # execute all other hooks to obtain the report object
    outcome = yield
    rep = outcome.get_result()

    # set an report attribute for each phase of a call, which can
    # be "setup", "call", "teardown"
    setattr(item, "rep_" + rep.when, rep)

def final_report():
    end_time = get_current_time_iso_utc(adjust_seconds=1)
    start = urllib.parse.quote(start_time)
    end = urllib.parse.quote(end_time)
    project = DSN.split('/')[-1]
    print()
    print(f'GENERATED errors: https://testorg-az.sentry.io/issues/?query=se%3A{SE_TAG}+%21project%3Ajob-monitor-application-monitoring&start={start}&end={end}')
    print(f'OWN errors:       https://testorg-az.sentry.io/issues/?project={project}&query=se%3A{SE_TAG}&start={start}&end={end}')

atexit.register(final_report)

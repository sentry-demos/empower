import pytest
from os import environ
import os
import release_version_manager as ReleaseVersion

from selenium import webdriver
from appium import webdriver as appiumdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.remote.remote_connection import RemoteConnection

import sentry_sdk
from dotenv import load_dotenv
load_dotenv()

SAUCELABS_PROTOCOL = "https://"
DSN = os.getenv("DSN")
ENVIRONMENT = os.getenv("ENVIRONMENT") or "production"

# print("ENV", ENVIRONMENT)
# print("DSN", DSN)

import urllib3
urllib3.disable_warnings()

sentry_sdk.init(
    dsn="https://f4726f34778044bba8e826740f0e09ac@o87286.ingest.sentry.io/4504052300578816",
    traces_sample_rate=0,
    environment="dev",
)

desktop_browsers = [
    {
        "seleniumVersion": '3.4.0',
        "platform": "Windows 10",
        "browserName": "chrome",
        "version": "latest",
        "sauce:options": {}
    }, {
        "seleniumVersion": '3.4.0',
        "platform": "Windows 10",
        "browserName": "firefox",
        "version": "latest",
        "sauce:options": {}
    }, {
        "seleniumVersion": '3.4.0',
        "platform": "OS X 10.13",
        "browserName": "safari",
        "version": "latest-1",
        "sauce:options": {}
    }, {
        "seleniumVersion": '3.4.0',
        "platform": "OS X 10.13",
        "browserName": "chrome",
        "version": "latest",
        "sauce:options": {}
    }]

# sentry_sdk.capture_message("testing")

def pytest_addoption(parser):
    parser.addoption("--dc", action="store", default='us', help="Set Sauce Labs Data Center (US or EU)")

@pytest.fixture
def data_center(request):
    return request.config.getoption('--dc')

@pytest.fixture(params=desktop_browsers)
def desktop_web_driver(request, data_center):

    test_name = request.node.name
    build_tag = environ.get('BUILD_TAG', "Application-Monitoring-TDA")

    username = environ['SAUCE_USERNAME']
    access_key = environ['SAUCE_ACCESS_KEY']
    print("\nXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")
    if data_center and data_center.lower() == 'eu':
        selenium_endpoint = SAUCELABS_PROTOCOL + "{}:{}@ondemand.eu-central-1.saucelabs.com/wd/hub".format(username, access_key)
    else:
        selenium_endpoint = SAUCELABS_PROTOCOL + "{}:{}@ondemand.us-west-1.saucelabs.com/wd/hub".format(username, access_key)

    caps = dict()
    caps.update(request.param)
    caps['sauce:options'].update({'build': build_tag})
    caps['sauce:options'].update({'name': test_name})
    print("\nXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")
    browser = webdriver.Remote(
        command_executor=selenium_endpoint,
        desired_capabilities=caps,
        keep_alive=True
    )

    browser.implicitly_wait(10)

    sentry_sdk.set_tag("seleniumSessionId", browser.session_id)
    print("\nXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")
    # This is specifically for SauceLabs plugin.
    # In case test fails after selenium session creation having this here will help track it down.
    if browser is not None:
        print("SauceOnDemandSessionID={} job-name={}".format(browser.session_id, test_name))
    else:
        raise WebDriverException("Never created!")
    print("\nXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")
    yield browser

    # Teardown starts here
    # report results
    # use the test result to send the pass/fail status to Sauce Labs
    sauce_result = "failed" if request.node.rep_call.failed else "passed"

    # Handler failure scenario, send to Sentry job-monitor-application-monitoring
    if sauce_result == "failed":
        sentry_sdk.capture_message("Sauce Result: %s" % (sauce_result))
    print("\nXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")
    browser.execute_script("sauce:job-result={}".format(sauce_result))
    browser.quit()
    print("\nXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")
    # Handler done scenario, send to Sentry job-monitor-application-monitoring
    sentry_sdk.capture_message("Selenium Session Done")

@pytest.fixture
def android_react_native_emu_driver(request, data_center):

    username_cap = environ['SAUCE_USERNAME']
    access_key_cap = environ['SAUCE_ACCESS_KEY']
    release_version = ReleaseVersion.latest_react_native_github_release()

    caps = {
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
    }

    if data_center and data_center.lower() == 'eu':
        sauce_url = SAUCELABS_PROTOCOL + "{}:{}@ondemand.eu-central-1.saucelabs.com/wd/hub".format(username_cap, access_key_cap)
    else:
        sauce_url = SAUCELABS_PROTOCOL + "{}:{}@ondemand.us-west-1.saucelabs.com/wd/hub".format(username_cap, access_key_cap)

    driver = appiumdriver.Remote(sauce_url, desired_capabilities=caps)
    driver.implicitly_wait(20)
    yield driver
    sauce_result = "failed" if request.node.rep_call.failed else "passed"
    driver.execute_script("sauce:job-result={}".format(sauce_result))
    driver.quit()

@pytest.fixture
def android_emu_driver(request, data_center):

    username_cap = environ['SAUCE_USERNAME']
    access_key_cap = environ['SAUCE_ACCESS_KEY']
    release_version = ReleaseVersion.latest_android_github_release()

    caps = {
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
    }

    if data_center and data_center.lower() == 'eu':
        sauce_url = SAUCELABS_PROTOCOL + "{}:{}@ondemand.eu-central-1.saucelabs.com/wd/hub".format(username_cap, access_key_cap)
    else:
        sauce_url = SAUCELABS_PROTOCOL + "{}:{}@ondemand.us-west-1.saucelabs.com/wd/hub".format(username_cap, access_key_cap)

    driver = appiumdriver.Remote(sauce_url, desired_capabilities=caps)
    driver.implicitly_wait(20)
    yield driver
    sauce_result = "failed" if request.node.rep_call.failed else "passed"
    driver.execute_script("sauce:job-result={}".format(sauce_result))
    driver.quit()

@pytest.fixture
def ios_react_native_sim_driver(request, data_center):

    username_cap = environ['SAUCE_USERNAME']
    access_key_cap = environ['SAUCE_ACCESS_KEY']
    release_version = ReleaseVersion.latest_react_native_github_release()

    caps = {
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
    }

    if data_center and data_center.lower() == 'eu':
        sauce_url = SAUCELABS_PROTOCOL + "{}:{}@ondemand.eu-central-1.saucelabs.com/wd/hub".format(username_cap, access_key_cap)
    else:
        sauce_url = SAUCELABS_PROTOCOL + "{}:{}@ondemand.us-west-1.saucelabs.com/wd/hub".format(username_cap, access_key_cap)

    driver = appiumdriver.Remote(sauce_url, desired_capabilities=caps)
    driver.implicitly_wait(20)
    yield driver
    sauce_result = "failed" if request.node.rep_call.failed else "passed"
    driver.execute_script("sauce:job-result={}".format(sauce_result))
    driver.quit()

@pytest.fixture
def ios_sim_driver(request, data_center):

    username_cap = environ['SAUCE_USERNAME']
    access_key_cap = environ['SAUCE_ACCESS_KEY']
    release_version = ReleaseVersion.latest_ios_github_release()

    caps = {
        'username': username_cap,
        'accessKey': access_key_cap,
        'appium:deviceName': 'iPhone 11 Simulator',
        'platformName': 'iOS',
        'appium:platformVersion': '16.1',
        'udid':'157FB6DB-B28A-4BC1-8181-1524B31CE022',
        "appium:usePrebuiltWDA": "false",

        'sauce:options': {
            'appiumVersion': '1.21.0',
            'build': 'RDC-iOS-Mobile-Native',
            'name': request.node.name,
        },

        'appium:app': f'/Users/sergiolombana/Documents/saucelabs/EmpowerPlant.app',
    }

    if data_center and data_center.lower() == 'eu':
        sauce_url = SAUCELABS_PROTOCOL + "{}:{}@ondemand.eu-central-1.saucelabs.com/wd/hub".format(username_cap, access_key_cap)
    else:
        sauce_url = SAUCELABS_PROTOCOL + "{}:{}@ondemand.us-west-1.saucelabs.com/wd/hub".format(username_cap, access_key_cap)

    driver = appiumdriver.Remote('http://0.0.0.0:4723/wd/hub', desired_capabilities=caps)
    driver.implicitly_wait(20)
    yield driver

    #sauce_result = "passed"
    #driver.execute_script("sauce:job-result='passed'")
    #driver.execute_script("sauce:job-result={}".format(sauce_result))

    driver.quit()


@pytest.hookimpl(hookwrapper=True, tryfirst=True)
def pytest_runtest_makereport(item, call):
    # this sets the result as a test attribute for Sauce Labs reporting.
    # execute all other hooks to obtain the report object
    outcome = yield
    rep = outcome.get_result()

    # set an report attribute for each phase of a call, which can
    # be "setup", "call", "teardown"
    setattr(item, "rep_" + rep.when, rep)


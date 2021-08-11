import pytest
from os import environ
import os
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.remote.remote_connection import RemoteConnection

import sentry_sdk
from dotenv import load_dotenv
load_dotenv()
DSN = os.getenv("DSN")
ENVIRONMENT = os.getenv("ENVIRONMENT") or "production"
print("ENV", ENVIRONMENT)
print("DSN", DSN)

import urllib3
urllib3.disable_warnings()

sentry_sdk.init(
    dsn= DSN,
    traces_sample_rate=0,
    environment=ENVIRONMENT,
)

# Message captures for Selenium Sessions appear in order of browser/platform combos in this array.
browsers = [
    {
        "seleniumVersion": '3.4.0',
        "platform": "Windows 10",
        "browserName": "chrome",
        "version": "latest"
    }, {
        "seleniumVersion": '3.4.0',
        "platform": "Windows 10",
        "browserName": "firefox",
        "version": "latest"
    }, {
        "seleniumVersion": '3.4.0',
        "platform": "OS X 10.13",
        "browserName": "safari",
        "version": "latest-1"
    }, {
        "seleniumVersion": '3.4.0',
        "platform": "OS X 10.11",
        "browserName": "chrome",
        "version": "latest",
        "extendedDebugging": True
    }]

def pytest_generate_tests(metafunc):
    if 'driver' in metafunc.fixturenames:
        metafunc.parametrize('browser_config',
                             browsers,
                             ids=_generate_param_ids('broswerConfig', browsers),
                             scope='function')


def _generate_param_ids(name, values):
    return [("<%s:%s>" % (name, value)).replace('.', '_') for value in values]


@pytest.yield_fixture(scope='function')
def driver(request, browser_config):
    sentry_sdk.set_tag("seleniumPlatform", parsePlatform(request.node.name))
    sentry_sdk.set_tag("seleniumBrowser", parseBrowserName(request.node.name))

    # if the assignment below does not make sense to you please read up on object assignments.
    # The point is to make a copy and not mess with the original test spec.
    desired_caps = dict()
    desired_caps.update(browser_config)

    # Selenium WebDriver Connection
    test_name = request.node.name
    build_tag = environ.get('BUILD_TAG', None)
    tunnel_id = environ.get('TUNNEL_IDENTIFIER', None)
    username = environ.get('SAUCE_USERNAME', None)
    access_key = environ.get('SAUCE_ACCESS_KEY', None)

    selenium_endpoint = "https://%s:%s@ondemand.saucelabs.com:443/wd/hub" % (username, access_key)
    desired_caps['build'] = build_tag
    # we can move this to the config load or not, also messing with this on a test to test basis is possible :)
    desired_caps['tunnelIdentifier'] = tunnel_id
    desired_caps['name'] = test_name

    executor = RemoteConnection(selenium_endpoint, resolve_ip=False)
    browser = webdriver.Remote(
        command_executor=executor,
        desired_capabilities=desired_caps,
        keep_alive=True
    )
    browser.implicitly_wait(10)

    sentry_sdk.set_tag("seleniumSessionId", browser.session_id)

    # This is specifically for SauceLabs plugin.
    # In case test fails after selenium session creation having this here will help track it down.
    # creates one file per test non ideal but xdist is awful
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

    # If the test errors on not finding a button, then this should still execute
    # because it's part of Teardown which always runs
    sentry_sdk.set_tag("session_id", browser.session_id)
    sentry_sdk.capture_message("Selenium Session Done")


@pytest.hookimpl(hookwrapper=True, tryfirst=True)
def pytest_runtest_makereport(item, call):
    # this sets the result as a test attribute for Sauce Labs reporting.
    # execute all other hooks to obtain the report object
    outcome = yield
    rep = outcome.get_result()

    # set an report attribute for each phase of a call, which can
    # be "setup", "call", "teardown"
    setattr(item, "rep_" + rep.when, rep)

def parsePlatform(requestNodeName):
    platform = ""
    if "windows" in requestNodeName.lower():
        platform = "Windows"
    else:
        platform = "OSX"
    return platform

def parseBrowserName(requestNodeName):
    browserName = ""
    if "chrome" in requestNodeName.lower():
        browserName = "chrome"
    if "firefox" in requestNodeName.lower():
        browserName = "firefox"
    if "safari" in requestNodeName.lower():
        browserName = "safari"
    return browserName
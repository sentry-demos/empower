import pytest
from os import environ
import contextlib
import os
import release_version_manager as ReleaseVersion
import random as real_random
import subprocess
import urllib.parse
import atexit
import yaml
from typing import NamedTuple

from selenium import webdriver
from appium import webdriver as appiumdriver
from appium.options.android import UiAutomator2Options
from appium.options.ios import XCUITestOptions
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.safari.options import Options as SafariOptions
from datetime import datetime, timedelta, timezone
from urllib.parse import urlencode

import sentry_sdk

def get_system_user():
    return subprocess.check_output(['id', '-un']).strip().decode()

# Get current timestamp, with +/- adjustment if desired, as string in ISO format (for Sentry URLs)
# round seconds down (floor): adjust_seconds = 0
# round seconds up (ceil): adjust_seconds = 1
def get_current_time_iso_utc(adjust_seconds=0):
    dt = datetime.now(timezone.utc).replace(microsecond=0) + timedelta(seconds = adjust_seconds)
    return dt.strftime('%Y-%m-%dT%H:%M:%S')


# Example command usage:
#
#   SE_TAG=tda-my-new-test BATCH_SIZE=10 py.test -n 6 desktop_web
#

start_time = get_current_time_iso_utc()


class Browser(NamedTuple):
    remote: bool
    browserName: str
    browserVersion: str | None = None
    platformName: str | None = None

    @property
    def param_display(self) -> str:
        if self.remote:
            return f'{self.browserName}@{self.browserVersion}({self.platformName})'
        else:
            return f'{self.browserName}(local)'


class Config(NamedTuple):
    browsers: tuple[Browser, ...]
    dsn: str
    react_endpoints: tuple[str, ...]
    vue_endpoints: tuple[str, ...]


def _config() -> Config:
    cfg_filename = os.environ.get('TDA_CONFIG', 'config.yaml')
    with open(cfg_filename) as f:
        contents = yaml.safe_load(f)
    return Config(
        browsers=tuple(Browser(**d) for d in contents['browsers']),
        dsn=contents['dsn'],
        react_endpoints=tuple(contents['react_endpoints']),
        vue_endpoints=tuple(contents['vue_endpoints']),
    )

CONFIG = _config()

ENVIRONMENT = os.getenv("ENVIRONMENT") or "production"
# SE_TAG will be both:
#
# 1. Passed on to desktop_web as ?se= URL parameter so will show up in
# application-monitoring-* project issues generated as a result of running the test
#
# 2. Used for internal reporting of this test automation's own errors (to DSN above,
# i.e. "empower-tda" project)
#
# If no value is provided will attemptq

SE_TAG = os.getenv("SE_TAG") or get_system_user()

#
# random will be truly random, not seeded, when SE_TAG == 'tda'
#
MAGIC_SE = 'tda'

# BATCH_SIZE can be either <NUMBER> or random_<NUMBER>
# The later means each time a test is run the inner steps will be repeated a random
# number of times between 0 and <NUMBER> - 1
# e.g. BATCH_SIZE=5, or BATCH_SIZE=random_100
# IS_CANARY always overrides BATCH_SIZE
BATCH_SIZE = os.getenv("IS_CANARY") and "1" or (os.getenv("BATCH_SIZE") or "1")

SLEEP_LENGTH = os.getenv("SLEEP_LENGTH") or "random_2_1"

BACKENDS = (os.getenv("BACKENDS") or "flask,express,springboot,ruby,laravel,rails,aspnetcore").split(',')

import urllib3
urllib3.disable_warnings()

sentry_sdk.init(
    dsn=CONFIG.dsn,
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
desktop_browsers_ids = [
    '{browserName}@{browserVersion}({platformName})'.format(**browser)
    for browser in desktop_browsers
]

def pytest_addoption(parser):
    parser.addoption("--dc", action="store", default='us', help="Set Sauce Labs Data Center (US or EU)")

@pytest.fixture
def data_center(request):
    return request.config.getoption('--dc')

@pytest.fixture
def random(request):
    if SE_TAG != MAGIC_SE:
        # Ensure tests produce repeatable outcomes when re-run, see:
        cwd = os.path.dirname(os.path.realpath(__file__)) + '/'
        test_relpath = str(request.path).split(cwd)[1]
        # e.g: desktop_web/test_mytest.py:test_myfunction[desktop_web_driver0]
        seed = f'{test_relpath}:{request.node.name}'
        # Use a new Random object doesn't share state with global random generator
        # this is just in case some package uses global random in a way that would
        # upset repeatability (e.g. numer of random() calls varies b/w executions)
        return real_random.Random(seed)
    else:
        return real_random

# random_1.5
# random_3_1.0
# 5.5
@pytest.fixture
def sleep_length(random):
    def random_sleep_length():
        if SLEEP_LENGTH.startswith("random_"):
            spl = SLEEP_LENGTH.split('_')
            r = random.randrange(float(spl[1]))
            if len(spl) == 3:
                r += float(spl[2])
            return r
        else:
            r = random.random() # unused, to make sure we call random same number of times
            return float(SLEEP_LENGTH)
    return random_sleep_length


@pytest.fixture
def batch_size(random):
    if BATCH_SIZE.startswith("random_"):
        return random.randrange(int(BATCH_SIZE.split('_')[1]))
    else:
        r = random.random() # unused, to make sure we call random same number of times
        return int(BATCH_SIZE)

@pytest.fixture
def backend(random):
    def random_backend(exclude=[], include=[]):
        if not include:
            include = BACKENDS
        else:
            include = [include] if isinstance(include, str) else include

        exclude = [exclude] if isinstance(exclude, str) else exclude
        # Must sort to get same order across processes to ensure that seeded random.sample()
        # always returns the same values.
        # python3
        #   >>> list(set(['b', 'a', 'f', 'd', 'e', 'c']) - set(['c', 'a']))
        #   ['b', 'd', 'e', 'f']
        #   >>> list(set(['b', 'a', 'f', 'd', 'e', 'c']) - set(['c', 'a']))
        #   ['b', 'd', 'e', 'f']
        #   >>> exit()
        # python3
        #   >>> list(set(['b', 'a', 'f', 'd', 'e', 'c']) - set(['c', 'a']))
        #   ['d', 'f', 'b', 'e']
        backends = sorted(list(set(include) - set(exclude)))
        return random.sample(backends, 1)[0]
    return random_backend

@pytest.fixture
def endpoints():
    return CONFIG

# Automatically append a set of extra parameters to all URLs
#
#   remote = RemoteWithExtraUrlParams(..., extra_params='se=tda')
#   remote.get('https://google.com/')
#       -> webdriver.Remote.get(https://google.com/?se=tda)
class RemoteWithExtraUrlParams(webdriver.Remote):
    def __init__(self, *args, **kwargs):
        if 'extra_params' in kwargs:
            if kwargs['extra_params'].startswith(('&', '?')):
                raise ValueError('extra_params must be in format: "param1=value1&param2=value2..."')
            self.extra_params = kwargs['extra_params']
            del kwargs['extra_params']
        else:
            self.extra_params = None
        super().__init__(*args, **kwargs)

    def get(self, url):
        if self.extra_params:
            url += ('?' in url and '&' or '?') + self.extra_params
        super().get(url)

@pytest.fixture
def selenium_endpoint(data_center):
    username = environ['SAUCE_USERNAME']
    access_key = environ['SAUCE_ACCESS_KEY']

    if data_center and data_center.lower() == 'eu':
        return "https://{}:{}@ondemand.eu-central-1.saucelabs.com/wd/hub".format(username, access_key)
    else:
        return "https://{}:{}@ondemand.us-west-1.saucelabs.com/wd/hub".format(username, access_key)

@pytest.fixture
def set_tags(request):
    # request.fixturenames: Names of all active fixtures in this request.
    # e.g value: ['android_emu_driver', 'request', 'set_tags', 'selenium_endpoint', 'data_center']
    # NOTE: we depend on driver fixtures following *_driver naming convention here
    driver_name = list(filter(lambda x: x.endswith('_driver'), request.fixturenames))[0]
    # request.node: Underlying collection node (depends on current request scope).
    # e.g name: test_myfunction[desktop_web_driver0]
    test_name = request.node.name.split('[')[0]
    platform = driver_name.replace('_emu_driver', '').replace('_sim_driver', '').replace('_driver','')
    sentry_sdk.set_tag("pytestPlatform", platform)
    sentry_sdk.set_tag("pytestName", test_name)


@contextlib.contextmanager
def _sauce_browser(request, selenium_endpoint):
    try:
        test_name = request.node.name
        build_tag = environ.get('BUILD_TAG', "Application-Monitoring-TDA")

        options = _browser2class[request.param.browserName]()
        options.set_capability('platformName', request.param.platformName)
        options.set_capability('browserVersion', request.param.browserVersion)
        options.set_capability('sauce:options', {
            'seleniumVersion': '4.8.0',
            'build': build_tag,
            'name': test_name
        })

        browser = RemoteWithExtraUrlParams(
            command_executor=selenium_endpoint,
            options=options,
            keep_alive=True,
            # Note: these tags might not be supported by some frontends, e.g. Vue
            extra_params=urlencode({'se': SE_TAG})
        )

        browser.implicitly_wait(10)

        sentry_sdk.set_tag("seleniumSessionId", browser.session_id)

        # This is specifically for SauceLabs plugin.
        # In case test fails after selenium session creation having this here will help track it down.
        if browser is not None:
            print("SauceOnDemandSessionID={} job-name={}".format(browser.session_id, test_name))
        else:
            raise WebDriverException("Never created!")

        try:
            yield browser
        finally:
            # Teardown starts here
            # report results
            # use the test result to send the pass/fail status to Sauce Labs
            sauce_result = "failed" if request.node.rep_call.failed else "passed"

            # Handler failure scenario, send to Sentry empower-tda
            if sauce_result == "failed":
                sentry_sdk.capture_message("Sauce Result: %s" % (sauce_result))

            browser.execute_script("sauce:job-result={}".format(sauce_result))
            browser.quit()

            # desktop_web tests finished, send to Sentry empower-tda, look for tags pytestName, pytestPlatform, seleniumSessionId
            sentry_sdk.capture_message("Selenium Session Done")

    except Exception as err:
        sentry_sdk.capture_exception(err)


@contextlib.contextmanager
def _local_browser(request):
    assert request.param.browserName == 'chrome'  # TODO: add others
    options = webdriver.ChromeOptions()
    options.add_argument("no-sandbox")
    options.add_argument("disable-gpu")
    options.add_argument("disable-dev-shm-usage")
    options.add_argument("headless")
    with webdriver.Chrome(options=options) as driver:
        yield driver


@pytest.fixture(params=CONFIG.browsers, ids=[b.param_display for b in CONFIG.browsers])
def desktop_web_driver(request, set_tags):
    if request.param.remote:
        with _sauce_browser(request, request.getfixturevalue('selenium_endpoint')) as b:
            yield b
    else:
        with _local_browser(request) as b:
            yield b

@pytest.fixture
def android_react_native_emu_driver(request, set_tags, selenium_endpoint):

    try:
        release_version = ReleaseVersion.latest_react_native_github_release()

        options = UiAutomator2Options().load_capabilities({
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

        driver = appiumdriver.Remote(selenium_endpoint, options=options)
        driver.implicitly_wait(20)

        sentry_sdk.set_tag("seleniumSessionId", driver.session_id)

        yield driver
        sauce_result = "failed" if request.node.rep_call.failed else "passed"
        driver.execute_script("sauce:job-result={}".format(sauce_result))
        driver.quit()

        # android_react_native tests finished, send to Sentry empower-tda, look for tags pytestName, pytestPlatform, seleniumSessionId
        sentry_sdk.capture_message("Selenium Session Done")

    except Exception as err:
        sentry_sdk.capture_exception(err)

@pytest.fixture
def android_emu_driver(request, set_tags, selenium_endpoint):

    try:
        release_version = ReleaseVersion.latest_android_github_release()

        options = UiAutomator2Options().load_capabilities({
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

        driver = appiumdriver.Remote(selenium_endpoint, options=options)
        driver.implicitly_wait(20)

        sentry_sdk.set_tag("seleniumSessionId", driver.session_id)

        yield driver
        sauce_result = "failed" if request.node.rep_call.failed else "passed"
        driver.execute_script("sauce:job-result={}".format(sauce_result))
        driver.quit()

        # android tests finished, send to Sentry empower-tda, look for tags pytestName, pytestPlatform, seleniumSessionId
        sentry_sdk.capture_message("Selenium Session Done")

    except Exception as err:
        sentry_sdk.capture_exception(err)
        raise

@pytest.fixture
def ios_react_native_sim_driver(request, set_tags, selenium_endpoint):

    try:
        release_version = ReleaseVersion.latest_react_native_github_release()

        options = XCUITestOptions().load_capabilities({
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

        driver = appiumdriver.Remote(selenium_endpoint, options=options)
        driver.implicitly_wait(20)

        sentry_sdk.set_tag("seleniumSessionId", driver.session_id)

        yield driver
        sauce_result = "failed" if request.node.rep_call.failed else "passed"
        driver.execute_script("sauce:job-result={}".format(sauce_result))
        driver.quit()

        # ios_react_native tests finished, send to Sentry empower-tda, look for tags pytestName, pytestPlatform, seleniumSessionId
        sentry_sdk.capture_message("Selenium Session Done")

    except Exception as err:
        sentry_sdk.capture_exception(err)

@pytest.fixture
def ios_sim_driver(request, set_tags, selenium_endpoint):

    try:
        release_version = ReleaseVersion.latest_ios_github_release()

        options = XCUITestOptions().load_capabilities({
            'appium:deviceName': 'iPhone 13 Simulator',
            'platformName': 'iOS',
            'appium:platformVersion': '15.5',

            'sauce:options': {
                'appiumVersion': '1.22.3',
                'build': 'RDC-iOS-Mobile-Native',
                'name': request.node.name,
            },
            'appium:app': f'https://github.com/sentry-demos/ios/releases/download/{release_version}/EmpowerPlant_release.zip',
        })

        driver = appiumdriver.Remote(selenium_endpoint, options=options)
        driver.implicitly_wait(20)

        sentry_sdk.set_tag("seleniumSessionId", driver.session_id)

        yield driver
        sauce_result = "failed" if request.node.rep_call.failed else "passed"
        driver.execute_script("sauce:job-result={}".format(sauce_result))
        driver.quit()

        # ios tests finished, send to Sentry empower-tda, look for tags pytestName, pytestPlatform, seleniumSessionId
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

if 'localhost' not in CONFIG.dsn:
    def final_report():
        end_time = get_current_time_iso_utc(adjust_seconds=1)
        start = urllib.parse.quote(start_time)
        end = urllib.parse.quote(end_time)
        project = CONFIG.dsn.split('/')[-1]
        print()
        print(f'GENERATED errors: https://demo.sentry.io/issues/?query=se%3A{SE_TAG}+%21project%3Aempower-tda&start={start}&end={end}')
        print(f'OWN errors:       https://demo.sentry.io/issues/?project={project}&query=se%3A{SE_TAG}&start={start}&end={end}')

    atexit.register(final_report)

import time
import yaml
import random
import sentry_sdk
from urllib.parse import urlencode
from collections import OrderedDict

def test_about_employees(desktop_web_driver):
    sentry_sdk.set_tag("pytestName", "vue_test_about_employees")

    endpoint = "https://application-monitoring-vue-dot-sales-engineering-sf.appspot.com/about"

    sentry_sdk.set_tag("endpoint", endpoint)

    for i in range(random.randrange(20)):
        # TODO in application-monitoring/vue repo
        # should be able to click each employee and it navigates to an /:employee page
        # this demonstrates parameterized transactions in Vue

        try:
            desktop_web_driver.get(endpoint)

        except Exception as err:
            if err:
                sentry_sdk.capture_exception(err)

        time.sleep(random.randrange(2) + 1)

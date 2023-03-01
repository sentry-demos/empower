import time
import yaml
import pytest
import random
import sentry_sdk
from urllib.parse import urlencode
from collections import OrderedDict

def test_about_employees_vue(desktop_web_driver):
    sentry_sdk.set_tag("pytestName", "test_about_employees_vue")

    with open('endpoints.yaml', 'r') as stream:
        data_loaded = yaml.safe_load(stream)
        endpoints = data_loaded['vue_endpoints']

    for endpoint in endpoints:

        endpoint = endpoint + "/about"

        sentry_sdk.set_tag("endpoint", endpoint)

        for i in range(pytest.batch_size()):
            # TODO in application-monitoring/vue repo
            # should be able to click each employee and it navigates to an /:employee page
            # this demonstrates parameterized transactions in Vue

            try:
                desktop_web_driver.get(endpoint)

            except Exception as err:
                if err:
                    sentry_sdk.capture_exception(err)

            time.sleep(random.randrange(2) + 1)

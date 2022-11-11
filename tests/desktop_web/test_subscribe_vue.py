import time
import yaml
import random
import sentry_sdk
from urllib.parse import urlencode
from collections import OrderedDict

def test_subscribe_vue(desktop_web_driver):
    sentry_sdk.set_tag("pytestName", "test_subscribe_vue")

    with open('endpoints.yaml', 'r') as stream:
        data_loaded = yaml.safe_load(stream)
        endpoints = data_loaded['vue_endpoints']

    for endpoint in endpoints:
        
        endpoint = endpoint + "/subscribe"

        sentry_sdk.set_tag("endpoint", endpoint)

        for i in range(random.randrange(20)):

            try:
                desktop_web_driver.get(endpoint)

                # TODO the selector class should have same name as one in application/monitoring/React
                desktop_web_driver.find_element_by_css_selector('.subscribe-email-input').send_keys("sampleEmail@test.com")
                time.sleep(random.randrange(2) + 1)

                # TODO the selector class should have same name as one in application/monitoring/React
                desktop_web_driver.find_element_by_css_selector('.subscribe-button').click()
                time.sleep(random.randrange(2) + 1)

            except Exception as err:
                if err:
                    sentry_sdk.capture_exception(err)

            time.sleep(random.randrange(2) + 1)

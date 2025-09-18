import time
import pytest
import sentry_sdk
from collections import OrderedDict
from selenium.webdriver.common.by import By

def test_subscribe_vue(desktop_web_driver, endpoints, random, batch_size, sleep_length):

    for endpoint in [endpoints.vue_endpoint]:
        
        endpoint = endpoint + "/subscribe"

        sentry_sdk.set_tag("endpoint", endpoint)

        for i in range(batch_size):

            try:
                desktop_web_driver.get(endpoint)

                # TODO the selector class should have same name as one in application/monitoring/React
                desktop_web_driver.find_element(By.CSS_SELECTOR, '.subscribe-email-input').send_keys("sampleEmail@test.com")
                time.sleep(sleep_length())

                # TODO the selector class should have same name as one in application/monitoring/React
                desktop_web_driver.find_element(By.CSS_SELECTOR, '.subscribe-button').click()
                time.sleep(sleep_length())

            except Exception as err:
                if err:
                    sentry_sdk.capture_exception(err)

            time.sleep(sleep_length())

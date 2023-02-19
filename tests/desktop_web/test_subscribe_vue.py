import time
import pytest
import random
import sentry_sdk
from collections import OrderedDict
from selenium.webdriver.common.by import By

def test_subscribe_vue(desktop_web_driver, endpoints):
    sentry_sdk.set_tag("pytestName", "test_subscribe_vue")

    for endpoint in endpoints['vue_endpoints']:
        
        endpoint = endpoint + "/subscribe"

        sentry_sdk.set_tag("endpoint", endpoint)

        for i in range(pytest.batch_size()):

            try:
                desktop_web_driver.get(endpoint)

                # TODO the selector class should have same name as one in application/monitoring/React
                desktop_web_driver.find_element(By.CSS_SELECTOR, '.subscribe-email-input').send_keys("sampleEmail@test.com")
                time.sleep(random.randrange(2) + 1)

                # TODO the selector class should have same name as one in application/monitoring/React
                desktop_web_driver.find_element(By.CSS_SELECTOR, '.subscribe-button').click()
                time.sleep(random.randrange(2) + 1)

            except Exception as err:
                if err:
                    sentry_sdk.capture_exception(err)

            time.sleep(random.randrange(2) + 1)

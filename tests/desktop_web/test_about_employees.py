import time
import yaml
import random
import sentry_sdk
import pytest
from urllib.parse import urlencode

def test_about_employees(desktop_web_driver):
    sentry_sdk.set_tag("pytestName", "test_about_employees")

    with open('endpoints.yaml', 'r') as stream:
        data_loaded = yaml.safe_load(stream)
        endpoints = data_loaded['react_endpoints']

    for endpoint in endpoints:
        endpoint_about = endpoint + "/about"
        sentry_sdk.set_tag("endpoint", endpoint_about)

        # You can filter by se:tda in Sentry's UI as this will get set as a tag
        url = ""
        query_string = {
            'se': pytest.SE_TAG,
            'backend': pytest.random_backend()
        }
        url = endpoint_about + '?' + urlencode(query_string)

        employees = ["Jane Schmidt", "Lily Chan", "Keith Ryan", "Mason Kim", "Emma Garcia", "Noah Miller"]

        for i in range(random.randrange(20)):

            desktop_web_driver.get(url)

            # images are being loaded in /about from Cloud Storage
            time.sleep(random.randrange(2) + 1)

            # pick a random employee
            n = random.randrange(6)
            elementName = employees[n]

            employee_btn = desktop_web_driver.find_element_by_name(elementName)
            employee_btn.click()

            time.sleep(random.randrange(2) + 1)

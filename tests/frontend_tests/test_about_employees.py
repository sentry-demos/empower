import pytest
import time
import yaml
import random
import sentry_sdk

# This test is for the homepage '/' transaction
@pytest.mark.usefixtures("driver")
def test_about_employees(driver):
    sentry_sdk.set_tag("pytestName", "about_employees")

    with open('endpoints.yaml', 'r') as stream:
        data_loaded = yaml.safe_load(stream)
        endpoints = data_loaded['react_endpoints']

    for endpoint in endpoints:
        endpoint_about = endpoint + "/about"
        sentry_sdk.set_tag("endpoint", endpoint_about)

        # you can filter by se:tda in Sentry's UI
        # endpoint = endpoint + "?se=tda

        employees = ["Jane Schmidt", "Lily Chan", "Keith Ryan", "Mason Kim", "Emma Garcia", "Noah Miller"]

        # for i in range(random.randrange(20)):
        for i in range(10):
            driver.get(endpoint_about)
            
            # images are being loaded in /about from Cloud Storage
            time.sleep(random.randrange(2) + 1)
            
            n = random.randrange(6)
            elementName = employees[n]
            
            # employee_btn = driver.find_element_by_name("Jane Schmidt")
            employee_btn = driver.find_element_by_name(elementName)
            employee_btn.click()
            time.sleep(random.randrange(2) + 1)

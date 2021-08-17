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
        endpoint_products = endpoint + "/products"
        sentry_sdk.set_tag("endpoint", endpoint_products)

        # You can filter by se:tda in Sentry's UI as this will get set as a tag
        endpoint_products = endpoint_products + "?se=tda"

        # for i in range(random.randrange(20)):
        for i in range(10):
            driver.get(endpoint_products)

            # images are being loaded in /about from Cloud Storage
            time.sleep(random.randrange(2) + 1)

            products = driver.find_elements_by_css_selector('.products-list button')

            for i in range(4):
                n = random.randrange(2)
                products[n].click()
                time.sleep(2)


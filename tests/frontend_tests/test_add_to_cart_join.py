import pytest
import time
import yaml
import random

@pytest.mark.usefixtures("driver")
def test_add_to_cart_join(driver):
    sentry_sdk.set_tag("pytestName", "test_add_to_cart_join")

    with open('endpoints.yaml', 'r') as stream:
        data_loaded = yaml.safe_load(stream)
        endpoints = data_loaded['react_endpoints']

    for endpoint in endpoints:
        for i in range(random.randrange(20)):
            endpoint_products_join = endpoint + "/products-join"
            driver.get(endpoint_products_join)
            time.sleep(random.randrange(3) + 3)

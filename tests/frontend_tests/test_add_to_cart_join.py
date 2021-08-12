import pytest
import time
import yaml
import random
import sentry_sdk

@pytest.mark.usefixtures("driver")
def test_add_to_cart_join(driver):
    sentry_sdk.set_tag("pytestName", "test_add_to_cart_join")

    with open('endpoints.yaml', 'r') as stream:
        data_loaded = yaml.safe_load(stream)
        endpoints = data_loaded['react_endpoints']

    for endpoint in endpoints:
        endpoint_products_join = endpoint + "/products-join"
        sentry_sdk.set_tag("endpoint", endpoint_products_join)

        endpoint_products_join = endpoint_products_join + "?se=tda"
        
        for i in range(random.randrange(20)):
            driver.get(endpoint_products_join)
            time.sleep(random.randrange(3) + 3)

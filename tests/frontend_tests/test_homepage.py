import pytest
import time
import yaml
import random
import sentry_sdk

@pytest.mark.usefixtures("driver")
def test_homepage(driver):
    sentry_sdk.set_tag("pytestName", "test_homepage")

    with open('endpoints.yaml', 'r') as stream:
        data_loaded = yaml.safe_load(stream)
        endpoints = data_loaded['react_endpoints']

    for endpoint in endpoints:
        sentry_sdk.set_tag("endpoint", endpoint)
        endpoint = endpoint + "?se=tda&crash=0.2"
        for i in range(random.randrange(20)):
            
            # Add queryParam crash=.5 and see how data is different
            # Run once - how many /products /products-join python
            # Run once - how many /products /products-join python, if no sleep timeouts

            # Unique fingerprints somewhere, somehow...
            driver.get(endpoint)
            time.sleep(random.randrange(3) + 3)
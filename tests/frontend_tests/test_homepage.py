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

        # for a Failure Rate between 1% and 40% of the homepage '/' transaction
        n = random.uniform(0.01, .04)

        # filter in Performance and Discover by 'se:tda'
        endpoint = endpoint + "?se=tda&crash=%s" % (n)
        
        # for i in range(random.randrange(20)):
        for i in range(10):
            
            # Add queryParam crash=.5 and see how data is different
            # Run once - how many /products /products-join python
            # Run once - how many /products /products-join python, if no sleep timeouts

            # Unique fingerprints somewhere, somehow...
            driver.get(endpoint)
            time.sleep(random.randrange(3) + 3)
import pytest
import time
import yaml
import random
import sentry_sdk

# This test is for the homepage '/' transaction
@pytest.mark.usefixtures("driver")
def test_homepage(driver):
    sentry_sdk.set_tag("pytestName", "test_homepage")

    with open('endpoints.yaml', 'r') as stream:
        data_loaded = yaml.safe_load(stream)
        endpoints = data_loaded['react_endpoints']

    for endpoint in endpoints:
        sentry_sdk.set_tag("endpoint", endpoint)

        # Randomize the Failure Rate between 1% and 40%
        n = random.uniform(0.01, .04)

        # you can filter by se:tda in Sentry's UI
        endpoint = endpoint + "?se=tda&crash=%s" % (n)
        
        for i in range(random.randrange(20)):
            driver.get(endpoint)
            time.sleep(random.randrange(3) + 3)
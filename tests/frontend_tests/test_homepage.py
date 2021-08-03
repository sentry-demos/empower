import pytest
import time
import yaml
import random

@pytest.mark.usefixtures("driver")
def test_add_to_cart(driver):

    with open('endpoints.yaml', 'r') as stream:
        data_loaded = yaml.safe_load(stream)
        endpoints = data_loaded['react_endpoints']

    for endpoint in endpoints:
        endpoint = endpoint + "?se=tda&crash=0.2"
        for i in range(random.randrange(20)):
            
            # Add queryParam crash=.5 and see how data is different

            # Run once - how many /products /products-join python
            # Run once - how many /products /products-join python, if no sleep timeouts

            # Unique fingerprints somewhere, somehow
            driver.get(endpoint)
            time.sleep(random.randrange(3) + 3)
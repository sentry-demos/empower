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
        for i in range(random.randrange(20)):
            driver.get(endpoint + "/products-join")
            time.sleep(random.randrange(3) + 3)

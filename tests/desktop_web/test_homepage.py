import time
import yaml
import random
import sentry_sdk

# This test is for the homepage '/' transaction
def test_homepage(desktop_web_driver):
    sentry_sdk.set_tag("pytestName", "test_homepage")

    with open('endpoints.yaml', 'r') as stream:
        data_loaded = yaml.safe_load(stream)
        endpoints = data_loaded['react_endpoints']

    for endpoint in endpoints:
        sentry_sdk.set_tag("endpoint", endpoint)

        # 0 Test this first, that it generally works
        # 0 Make sure will-express, will-springboot are getting Tx's+Errors, first. via localhost and/or App Engine instances.

        # 1 Refactor using a URL lib

        # you can filter by se:tda in Sentry's UI
        # TODO - could manage se, crash, backend QueryStrings via a .env file? config somewhere? conftest.py? Could re-purpose endpoints.yaml as config.yaml and do endpoints = data_loaded['se'], data_loaded['crash'], data_loaded['backends']
        endpoint = endpoint + "?se=will" # TODO undo this, when done

        # Randomize the Failure Rate between 1% and 40%
        n = random.uniform(0.01, .04)

        # This query string is parsed by utils/errors.js wherever the 'crasher' function is used
        # and causes the page to periodically crash, for Release Health
        endpoint = endpoint + "&crash=%s" % (n)

        # 2 Add backend queryString, backend=express, backend=springboot
        for i in range(random.randrange(20)):
            desktop_web_driver.get(endpoint)
            time.sleep(random.randrange(3) + 3)

        # 3 Check Discover for tda:will - did Express+Springboot transactions come through?
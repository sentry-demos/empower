import time
import yaml
import random
import sentry_sdk
from urllib.parse import urlencode
from collections import OrderedDict

# This test is for the homepage '/' transaction
def test_homepage(desktop_web_driver):
    sentry_sdk.set_tag("pytestName", "test_homepage")

    with open('endpoints.yaml', 'r') as stream:
        data_loaded = yaml.safe_load(stream)
        endpoints = data_loaded['react_endpoints']

    for endpoint in endpoints:
        sentry_sdk.set_tag("endpoint", endpoint)

        # you can filter by se:tda in Sentry's UI
        # endpoint = endpoint + "?se=will" # TODO undo this, when done

        # Randomize the Failure Rate between 1% and 40%
        n = random.uniform(0.01, .04)

        # This query string is parsed by utils/errors.js wherever the 'crasher' function is used
        # and causes the page to periodically crash, for Release Health
        # endpoint = endpoint + "&crash=%s" % (n)

        query_string = { 'se': 'will','crash': "%s" % (n)}
        endpoint = endpoint + '?' + urlencode(query_string)

        for i in range(random.randrange(20)):
            # TODO add /success call from Homepage so can put endpoint construction here, as it will take 1 of 3 random backends.
            # url = ""
            desktop_web_driver.get(endpoint)
            time.sleep(random.randrange(3) + 3)

        # TODO undo se:tda and put back to se:will
import time
import yaml
import random
import sentry_sdk
from urllib.parse import urlencode

def test_organization(desktop_web_driver):
    sentry_sdk.set_tag("pytestName", "test_organization")

    with open('endpoints.yaml', 'r') as stream:
        data_loaded = yaml.safe_load(stream)
        endpoints = data_loaded['react_endpoints']

    for endpoint in endpoints:
        endpoint_organization = endpoint + "/organization"
        sentry_sdk.set_tag("endpoint", endpoint_organization)

        # You can filter by se:tda in Sentry's UI as this will get set as a tag
        url = ""
        query_string = { 
            'se': 'tda',
        }
        url = endpoint_organization + '?' + urlencode(query_string)

        for i in range(random.randrange(20)):
        
            desktop_web_driver.get(url)

            # images are being loaded in /about from Cloud Storage
            time.sleep(random.randrange(2) + 1)
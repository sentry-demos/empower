import time
import random
import pytest
import sentry_sdk
from urllib.parse import urlencode

def test_organization(desktop_web_driver, endpoints):
    sentry_sdk.set_tag("pytestName", "test_organization")

    for endpoint in endpoints['react_endpoints']:
        endpoint_organization = endpoint + "/organization"
        sentry_sdk.set_tag("endpoint", endpoint_organization)

        # You can filter by se:tda in Sentry's UI as this will get set as a tag
        url = ""
        query_string = { 
            'se': pytest.SE_TAG,
        }
        url = endpoint_organization + '?' + urlencode(query_string)

        for i in range(pytest.batch_size()):
        
            desktop_web_driver.get(url)

            # images are being loaded in /about from Cloud Storage
            time.sleep(random.randrange(2) + 1)
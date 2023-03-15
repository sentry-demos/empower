import time
import pytest
import sentry_sdk

def test_organization(desktop_web_driver, endpoints, random, batch_size, sleep_length):

    for endpoint in endpoints['react_endpoints']:
        endpoint_organization = endpoint + "/organization"
        sentry_sdk.set_tag("endpoint", endpoint_organization)

        url = endpoint_organization

        for i in range(batch_size):
        
            desktop_web_driver.get(url)

            # images are being loaded in /about from Cloud Storage
            time.sleep(sleep_length())
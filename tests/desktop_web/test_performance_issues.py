import time
import pytest
import sentry_sdk

def test_nplusone(desktop_web_driver, endpoints, random, batch_size, sleep_length):
    sentry_sdk.set_tag("pytestName", "test_nplusone")

    for endpoint in endpoints['react_endpoints']:
        endpoint_organization = endpoint + "/nplusone"
        sentry_sdk.set_tag("endpoint", endpoint_organization)

        url = endpoint_organization

        for i in range(batch_size):

            desktop_web_driver.get(url)

            # images are being loaded in /about from Cloud Storage
            time.sleep(sleep_length())

import time
import sentry_sdk
import pytest
from urllib.parse import urlencode

def test_about_employees(desktop_web_driver, endpoints, random, batch_size, backend, sleep_length):

    for endpoint in endpoints.react_endpoints:
        endpoint_about = endpoint + "/about"
        sentry_sdk.set_tag("endpoint", endpoint_about)

        url = ""
        query_string = {
            'backend': backend()
        }
        url = endpoint_about + '?' + urlencode(query_string)

        employees = ["Jane Schmidt", "Lily Chan", "Keith Ryan", "Mason Kim", "Emma Garcia", "Noah Miller"]

        for i in range(batch_size):

            desktop_web_driver.get(url)

            # images are being loaded in /about from Cloud Storage
            time.sleep(sleep_length())

            # pick a random employee
            n = random.randrange(6)
            elementName = employees[n]

            employee_btn = desktop_web_driver.find_element("name", elementName)
            employee_btn.click()

            time.sleep(sleep_length())

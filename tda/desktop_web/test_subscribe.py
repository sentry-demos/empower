import time
import sentry_sdk
from urllib.parse import urlencode
from datetime import datetime
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException


def test_subscribe(desktop_web_driver, endpoints, batch_size, sleep_length, random=None):
    """
    A standalone test that navigates to each React endpoint, attempts an email
    subscription, and records success/failure to Sentry metrics.
    """
    for endpoint in endpoints.react_endpoints:
        # Tag each test iteration with the endpoint
        sentry_sdk.set_tag("endpoint", endpoint)

        # Flask backend is the only one that supports email subscriptions queueing 
        query_string = {
          'backend': 'flask'
        }

        url = endpoint + '?' + urlencode(query_string)

        for i in range(batch_size):
            try:
                # Navigate to the page
                desktop_web_driver.get(url)

                # Give the page some time to load (increase if needed)
                time.sleep(sleep_length())

                # Locate the email input field and enter a sample address
                email_input = desktop_web_driver.find_element(By.CSS_SELECTOR, '#email-subscribe')
                email_input.send_keys("mySampleEmail@example.com")

                # Locate and click the "Subscribe" button
                subscribe_btn = desktop_web_driver.find_element(By.CSS_SELECTOR, '.subscribe-button')
                subscribe_btn.click()

                # Wait to allow any subsequent requests to finish
                time.sleep(sleep_length())


            except NoSuchElementException as err:
                # If we can't find elements, count it as an abandoned iteration
                sentry_sdk.capture_exception(err)

            except Exception as err:
                # Catch all other errors
                sentry_sdk.capture_exception(err)

            # Sleep again at the end of each iteration if needed
            time.sleep(sleep_length())


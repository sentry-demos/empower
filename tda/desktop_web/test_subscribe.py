import time
import sentry_sdk
from urllib.parse import urlencode
from datetime import datetime
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException


def test_subscribe(desktop_web_driver, endpoints, batch_size, backend, sleep_length, random=None):
    """
    A standalone test that navigates to each React endpoint, attempts an email
    subscription, and records success/failure to Sentry metrics.
    """
    for endpoint in endpoints.react_endpoints:
        # Tag each test iteration with the endpoint
        sentry_sdk.set_tag("endpoint", endpoint)

        for i in range(batch_size):

            # Build a query string to pass the chosen backend, if your app needs it
            # for the subscription endpoint. Adjust as needed.
            query_string = {
                'backend': backend()
            }

            # Construct the final URL
            url = endpoint + '?' + urlencode(query_string)

            # Mark that the iteration started
            sentry_sdk.metrics.incr(
                key="test_subscribe.iteration.started",
                value=1,
                tags=query_string
            )

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

                subscribe_btn.click()

                time.sleep(3)

                # Mark completion in Sentry metrics
                sentry_sdk.metrics.incr(
                    key="test_subscribe.iteration.completed",
                    value=1,
                    tags=query_string
                )


            except NoSuchElementException as err:
                # If we can't find elements, count it as an abandoned iteration
                sentry_sdk.metrics.incr(
                    key="test_subscribe.iteration.abandoned",
                    value=1,
                    tags=dict(query_string, reason="no_subscribe_elements")
                )
                sentry_sdk.capture_exception(err)

            except Exception as err:
                # Catch all other errors
                sentry_sdk.metrics.incr(
                    key="test_subscribe.iteration.abandoned",
                    value=1,
                    tags=dict(query_string, reason=f"other({err.__class__.__name__})")
                )
                sentry_sdk.capture_exception(err)

            # Sleep again at the end of each iteration if needed
            time.sleep(sleep_length())


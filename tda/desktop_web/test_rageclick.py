import time
import sentry_sdk
from urllib.parse import urlencode
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException

# This many clicks to trigger rage click
# plus some extra for good measure (+ extra rage)
RAGE_CLICK_TRIGGER_QTY = 10

def test_rageclick(desktop_web_driver, endpoints, batch_size, backend, random, sleep_length):

    for endpoint in endpoints.react_endpoints:
        endpoint_products = endpoint + "/products"
        sentry_sdk.set_tag("endpoint", endpoint_products)

        missedButtons = 0

        for i in range(batch_size):
            # Ensures a different backend endpoint gets picked each time
            url = ""
            # TODO make a query_string builder function for sharing this across tests
            query_string = {
                # 'ruby' /products /checkout endpoints not available yet
                'backend': backend(exclude='ruby'),
                'rageclick': 'true'
            }
            url = endpoint_products + '?' + urlencode(query_string)

            # Buttons are not available if products didn't load before selection, so handle this
            try:
                desktop_web_driver.get(url)

                # Wait up to 2 implicit waits (should be 20 seconds)
                try:
                    desktop_web_driver.find_element(By.CSS_SELECTOR, '.products-list button').click()
                except TimeoutException as err:
                    desktop_web_driver.find_element(By.CSS_SELECTOR, '.products-list button').click()


                desktop_web_driver.find_element(By.CSS_SELECTOR, '.show-desktop #top-right-links a[href="/cart"]').click()
                desktop_web_driver.find_element(By.CSS_SELECTOR, 'a[href="/checkout"]').click()

                # Rage click
                checkout_button = desktop_web_driver.find_element(By.CSS_SELECTOR, '.complete-checkout-btn')
                for _ in range(RAGE_CLICK_TRIGGER_QTY):
                    checkout_button.click()
                time.sleep(8) #rageclick currently detected after 7 seconds

            except Exception as err:
                sentry_sdk.capture_exception(err)

            time.sleep(sleep_length())

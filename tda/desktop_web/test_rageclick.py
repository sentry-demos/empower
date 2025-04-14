import time
import sentry_sdk
from urllib.parse import urlencode
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

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
            query_string = {
                'backend': backend(exclude='ruby'),
                'rageclick': 'true'
            }
            url = endpoint_products + '?' + urlencode(query_string)

            try:
                desktop_web_driver.get(url)

                # Wait for and click product button
                product_button = WebDriverWait(desktop_web_driver, 20).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, '.products-list button'))
                )
                product_button.click()

                # Wait for and click cart link
                cart_link = WebDriverWait(desktop_web_driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, '.show-desktop #top-right-links a[href="/cart"]'))
                )
                cart_link.click()

                # Wait for and click checkout link
                checkout_link = WebDriverWait(desktop_web_driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, 'a[href="/checkout"]'))
                )
                checkout_link.click()

                # Wait for checkout button and perform rage clicks
                checkout_button = WebDriverWait(desktop_web_driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, '.complete-checkout-btn'))
                )
                for _ in range(RAGE_CLICK_TRIGGER_QTY):
                    checkout_button.click()
                    
                time.sleep(8) #rageclick currently detected after 7 seconds

            except Exception as err:
                sentry_sdk.capture_exception(err)

            time.sleep(sleep_length())

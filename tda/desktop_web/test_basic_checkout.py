import time
import sentry_sdk
from urllib.parse import urlencode
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException


def test_basic_checkout(desktop_web_driver, endpoints, random, sleep_length, cexp):
    for endpoint in [endpoints.nextjs_endpoint]:

        endpoint_products = endpoint + "/products"

        # to generate more flagship errors than Slow DB Query, other performance issues
        checkout_attempts = 3

        query_string = {}
        url = endpoint_products + '?' + urlencode(query_string)
        
        # Buttons are not available if products didn't load before selection, so handle this
        try:
            desktop_web_driver.get(url)

            try:
                # Wait up to 2 implicit waits (should be 20 seconds)
                try:
                    add_to_cart_btn = desktop_web_driver.find_element(By.CSS_SELECTOR, '.products-list button')
                except NoSuchElementException as err:
                    add_to_cart_btn = desktop_web_driver.find_element(By.CSS_SELECTOR, '.products-list button')

                for i in range(random.randrange(4) + 1):
                    add_to_cart_btn.click()
            except NoSuchElementException as err:
                continue

            # Add 2 second sleep between the initial /products pageload
            #   and the navigation to the checkout cart
            #   to solve for web vitals issue as transaction may not be resolving
            time.sleep(2)

            for c in range(checkout_attempts):
                desktop_web_driver.find_element(By.CSS_SELECTOR, '.show-desktop #top-right-links a[href="/cart"]').click()

                time.sleep(sleep_length())

                try:
                    desktop_web_driver.find_element(By.CSS_SELECTOR, 'a[href="/checkout"]').click()
                except NoSuchElementException as err:
                    continue

                time.sleep(sleep_length())
                
                desktop_web_driver.find_element(By.CSS_SELECTOR, '#email').send_keys("sampleEmail@email.com")

                desktop_web_driver.find_element(By.CSS_SELECTOR, '.complete-checkout-btn').click()
                time.sleep(sleep_length())

        except Exception as err:
            sentry_sdk.capture_exception(err)

        time.sleep(sleep_length())

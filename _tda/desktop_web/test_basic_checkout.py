import time
import pytest
import sentry_sdk
from urllib.parse import urlencode
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException


# Skip before desktop_web_driver so a 0-draw does not open a Sauce session.
@pytest.fixture(autouse=True)
def _skip_if_no_seasonal_volume(unit_seasonal_batch_size):
    if unit_seasonal_batch_size == 0:
        pytest.skip("seasonal skip")


def test_basic_checkout(desktop_web_driver, endpoints, random, sleep_length, cexp, unit_seasonal_batch_size):
    for endpoint in [endpoints.nextjs_endpoint, endpoints.angular_endpoint, endpoints.vue_endpoint]:

        endpoint_products = endpoint + "/products"

        sentry_sdk.set_tag("endpoint", endpoint_products)
        sentry_sdk.set_tag("batch_size", unit_seasonal_batch_size)

        for b in range(unit_seasonal_batch_size):
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
                        desktop_web_driver.find_element(By.CSS_SELECTOR, 'a[href="/checkout-form"]').click()
                    except NoSuchElementException as err:
                        continue

                    time.sleep(sleep_length())
                    
                    desktop_web_driver.find_element(By.CSS_SELECTOR, '#email').send_keys("sampleEmail@email.com")

                    desktop_web_driver.find_element(By.CSS_SELECTOR, '.complete-checkout-btn').click()
                    time.sleep(sleep_length())

            except Exception as err:
                sentry_sdk.capture_exception(err)

            time.sleep(sleep_length())

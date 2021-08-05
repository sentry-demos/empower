import pytest
import time
import yaml
import random
import sentry_sdk

# 'driver' is "<selenium.webdriver.remote.webdriver.WebDriver (session="3955e7dab66c4172ad3d4a8808c0a67c")>" if you print it
@pytest.mark.usefixtures("driver")
def test_add_to_cart(driver):
    sentry_sdk.set_tag("pytestName", "test_add_to_cart")

    with open('endpoints.yaml', 'r') as stream:
        data_loaded = yaml.safe_load(stream)
        endpoints = data_loaded['react_endpoints']

    for endpoint in endpoints:
        sentry_sdk.set_tag("endpoint", endpoint)
        missedButtons = 0

        for i in range(random.randrange(20)):

            # Buttons are not available if products didn't load before selection, so handle this
            try:
                endpoint_products = endpoint + "/products"
                driver.get(endpoint_products)

                # Wait for button to be loaded in (no randomizing the sleep, because randomizing the sleep statement does not affect any transaction or span durations. there's no observable benefit)
                time.sleep(5)

                add_to_cart_btn = driver.find_element_by_css_selector('.products-list button')
                for i in range(random.randrange(4) + 1):
                    add_to_cart_btn.click()

                driver.find_element_by_css_selector('.show-desktop #top-right-links a[href="/cart"]').click()
                time.sleep(random.randrange(2) + 1)
                driver.find_element_by_css_selector('a[href="/checkout"]').click()
                time.sleep(random.randrange(2) + 1)

                driver.find_element_by_css_selector('#email').send_keys("sampleEmail@email.com")
                time.sleep(random.randrange(2) + 1)

                driver.find_element_by_css_selector('.complete-checkout-btn').click()
                time.sleep(random.randrange(2) + 1)

            except Exception as err:
                missedButtons = missedButtons + 1
                sentry_sdk.set_tag("missedButtons", missedButtons)
                sentry_sdk.set_tag("seleniumSessionId", driver.session_id)
                
                if err:
                    sentry_sdk.capture_exception(err)

            time.sleep(random.randrange(2) + 1)











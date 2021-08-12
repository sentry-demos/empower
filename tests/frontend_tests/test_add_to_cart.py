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
        endpoint_products = endpoint + "/products"
        sentry_sdk.set_tag("endpoint", endpoint_products)

        endpoint_products = endpoint_products + "?se=tda"
        
        missedButtons = 0

        for i in range(random.randrange(20)):

            # Buttons are not available if products didn't load before selection, so handle this
            try:
                driver.get(endpoint_products)

                # Optional - use the time.sleep here so button can rinish rendering before the driver tries to click it
                # Solution - handle gracefully when the driver clicks a button that's not rendered yet, and then time.sleep(1) and try again
                # time.sleep(5)

                buttonRendered = False
                skips=0
                while buttonRendered==False:
                    try:
                        if skips > 10:
                            sentry_sdk.capture_message("missed button more than 10 skips")
                            buttonRendered=True
                        add_to_cart_btn = driver.find_element_by_css_selector('.products-list button')
                        for i in range(random.randrange(4) + 1):
                            add_to_cart_btn.click()
                        buttonRendered=True
                    except Exception as err:
                        skips = skips + 1
                        sentry_sdk.capture_message("missed button handling %s skips gracefully" % (skips))
                        time.sleep(1)
                        pass

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











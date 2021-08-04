import pytest
import time
import yaml
import random
import sentry_sdk

# If you print 'driver', it's not an object, it's "<selenium.webdriver.remote.webdriver.WebDriver (session="3955e7dab66c4172ad3d4a8808c0a67c")>"
@pytest.mark.usefixtures("driver")
def test_add_to_cart(driver):
    sentry_sdk.set_tag("pytestName", "test_add_to_cart")
    
    # print("> driver.session_id", driver.session_id) # NOT NEEDED?
    # print("> driver.getSessionId()", driver.getSessionId()) # FAILED


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

                # EVAL - Wait for button to be loaded in
                time.sleep(random.randrange(3) + 3)

                # TODO If "Unable to locate element", then sleep,wait, try again...
                add_to_cart_btn = driver.find_element_by_css_selector('.products-list button')
                for i in range(random.randrange(3) + 3):
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
                print("> err", err)
                missedButtons = missedButtons + 1
                sentry_sdk.set_tag("missedButtons", missedButtons)
                # raise SystemExit(err) <-- instead, look at SeleniumSessionDone | Sauce Result Failed

            time.sleep(random.randrange(2) + 1)











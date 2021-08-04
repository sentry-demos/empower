import pytest
import time
import yaml
import random

@pytest.mark.usefixtures("driver")
def test_add_to_cart(driver):
    sentry_sdk.set_tag("pytestName", "test_add_to_cart")
    
    with open('endpoints.yaml', 'r') as stream:
        data_loaded = yaml.safe_load(stream)
        endpoints = data_loaded['react_endpoints']

    for endpoint in endpoints:
        for i in range(random.randrange(20)):
            # EVAL, realized late that this was here...
            # driver.get(endpoint)

            try:
                endpoint_products = endpoint + "/products"
                driver.get(endpoint_products)

                # EVAL
                # Wait for button to be loaded in
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
                    raise SystemExit(err)

            time.sleep(random.randrange(2) + 1)











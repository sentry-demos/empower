import pytest
import time
import yaml
import random

@pytest.mark.usefixtures("driver")
def test_add_to_cart(driver):

    with open('endpoints.yaml', 'r') as stream:
        data_loaded = yaml.safe_load(stream)
        endpoints = data_loaded['react_endpoints']

    for endpoint in endpoints:
        for i in range(random.randrange(20)):
            driver.get(endpoint)

            browse_btn = driver.find_element_by_css_selector('.btn')
            browse_btn.click()

            add_to_cart_btn = driver.find_element_by_css_selector('.products-list button')
            for i in range(random.randrange(3) + 3):
                add_to_cart_btn.click()

            driver.find_element_by_css_selector('.show-desktop #top-right-links a[href="/cart"]').click()
            time.sleep(random.randrange(3) + 3)
            driver.find_element_by_css_selector('a[href="/checkout"]').click()
            time.sleep(random.randrange(3) + 3)

            # TODO dynamically fill out all fields
            driver.find_element_by_css_selector('#email').send_keys("sampleEmail@email.com")
            time.sleep(random.randrange(3) + 3)

            driver.find_element_by_css_selector('.complete-checkout-btn').click()
            time.sleep(random.randrange(3) + 3)









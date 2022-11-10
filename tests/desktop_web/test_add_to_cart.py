import time
import yaml
import random
import sentry_sdk
from urllib.parse import urlencode

def test_add_to_cart(desktop_web_driver):
    sentry_sdk.set_tag("pytestName", "test_add_to_cart")

    with open('endpoints.yaml', 'r') as stream:
        data_loaded = yaml.safe_load(stream)
        endpoints = data_loaded['react_endpoints']

    for endpoint in endpoints:
        endpoint_products = endpoint + "/products"
        sentry_sdk.set_tag("endpoint", endpoint_products)

        missedButtons = 0

        for i in range(random.randrange(20)):
            # Ensures a different backend endpoint gets picked each time
            url = ""
            # TODO make a query_string builder function for sharing this across tests
            query_string = { 
                'se': 'tda',
                # 'ruby' /products /checkout endpoints not available yet
                'backend': random.sample(['flask', 'express','springboot'], 1)[0]
            }
            url = endpoint_products + '?' + urlencode(query_string)

            # Buttons are not available if products didn't load before selection, so handle this
            try:
                desktop_web_driver.get(url)

                # Optional - use the time.sleep here so button can rinish rendering before the desktop_web_driver tries to click it
                # Solution - handle gracefully when the desktop_web_driver clicks a button that's not rendered yet, and then time.sleep(1) and try again
                # time.sleep(5)

                buttonRendered = False
                skips=0
                while buttonRendered==False:
                    try:
                        if skips > 10:
                            sentry_sdk.capture_message("missed button more than 10 skips")
                            buttonRendered=True
                        add_to_cart_btn = desktop_web_driver.find_element_by_css_selector('.products-list button')
                        for i in range(random.randrange(4) + 1):
                            add_to_cart_btn.click()
                        buttonRendered=True
                    except Exception as err:
                        skips = skips + 1
                        sentry_sdk.capture_message("missed button handling %s skips gracefully" % (skips))
                        time.sleep(1)
                        pass

                desktop_web_driver.find_element_by_css_selector('.show-desktop #top-right-links a[href="/cart"]').click()
                time.sleep(random.randrange(2) + 1)
                desktop_web_driver.find_element_by_css_selector('a[href="/checkout"]').click()
                time.sleep(random.randrange(2) + 1)

                desktop_web_driver.find_element_by_css_selector('#email').send_keys("sampleEmail@email.com")
                time.sleep(random.randrange(2) + 1)

                desktop_web_driver.find_element_by_css_selector('.complete-checkout-btn').click()
                time.sleep(random.randrange(2) + 1)

            except Exception as err:
                missedButtons = missedButtons + 1
                sentry_sdk.set_tag("missedButtons", missedButtons)

                if err:
                    sentry_sdk.capture_exception(err)

            time.sleep(random.randrange(2) + 1)











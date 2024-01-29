import time
import sentry_sdk
from urllib.parse import urlencode
from selenium.webdriver.common.by import By

def test_checkout(desktop_web_driver, endpoints, batch_size, backend, random, sleep_length):

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
                'backend': backend(exclude='ruby')
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
                        add_to_cart_btn = desktop_web_driver.find_element(By.CSS_SELECTOR, '.products-list button')
                        time.sleep(2)
                        for i in range(random.randrange(4) + 1):
                            add_to_cart_btn.click()
                        buttonRendered=True
                    except Exception as err:
                        skips = skips + 1
                        sentry_sdk.capture_message("missed button handling %s skips gracefully" % (skips))
                        time.sleep(1)
                        pass

                # Add 2 second sleep between the initial /products pageload
                #   and the navigation to the checkout cart
                #   to solve for web vitals issue as transaction may not be resolving
                time.sleep(2)

                desktop_web_driver.find_element(By.CSS_SELECTOR, '.show-desktop #top-right-links a[href="/cart"]').click()
                time.sleep(sleep_length())
                desktop_web_driver.find_element(By.CSS_SELECTOR, 'a[href="/checkout"]').click()
                time.sleep(sleep_length())

                desktop_web_driver.find_element(By.CSS_SELECTOR, '#email').send_keys("sampleEmail@email.com")

                desktop_web_driver.find_element(By.CSS_SELECTOR, '.complete-checkout-btn').click()
                time.sleep(sleep_length())

            except Exception as err:
                missedButtons = missedButtons + 1
                sentry_sdk.set_tag("missedButtons", missedButtons)

                if err:
                    sentry_sdk.capture_exception(err)

            time.sleep(sleep_length())











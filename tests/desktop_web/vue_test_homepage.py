import time
import yaml
import random
import sentry_sdk
from urllib.parse import urlencode
from collections import OrderedDict

# This test is for the homepage '/' transaction
def vue_test_homepage(desktop_web_driver):
    sentry_sdk.set_tag("pytestName", "vue_test_homepage")

    endpoint = "https://application-monitoring-vue-dot-sales-engineering-sf.appspot.com/"

    sentry_sdk.set_tag("endpoint", endpoint)

    missedButtons = 0

    # TODO CHANGE back to range(random.randrange(20)) when done testing
    for i in range(5):
        # TODO 
        # querystring support for 'se' and 'backend' tags
        
        # TODO
        # No randomization of failures, because Vue app is not setup to do this right now.

        # TODO
        # "/products" not needed right now, because Home page in Vue app loads the products

        # Buttons are not available if products didn't load before selection, so handle this
        try:
            desktop_web_driver.get(endpoint)

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
            # TODO the Vue app class should be .complete-checkout-btn so it matches the React app
            desktop_web_driver.find_element_by_css_selector('.checkout-button').click()
            time.sleep(random.randrange(2) + 1)

        except Exception as err:
            missedButtons = missedButtons + 1
            sentry_sdk.set_tag("missedButtons", missedButtons)
            sentry_sdk.set_tag("seleniumSessionId", desktop_web_driver.session_id)

            if err:
                sentry_sdk.capture_exception(err)

        time.sleep(random.randrange(2) + 1)

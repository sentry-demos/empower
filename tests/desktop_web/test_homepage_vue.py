import time
import yaml
import pytest
import random
import sentry_sdk
from urllib.parse import urlencode
from collections import OrderedDict
from selenium.webdriver.common.by import By

# Note: Not sure why won't pytest find this and run it when I name it 'vue_test_homepage'
def test_homepage_vue(desktop_web_driver):
    sentry_sdk.set_tag("pytestName", "test_homepage_vue")

    with open('endpoints.yaml', 'r') as stream:
        data_loaded = yaml.safe_load(stream)
        endpoints = data_loaded['vue_endpoints']

    for endpoint in endpoints:

        # TODO homepage endpoint loads Products but in future will need to append /products to the endpoint
        sentry_sdk.set_tag("endpoint", endpoint)

        missedButtons = 0

        for i in range(pytest.batch_size()):
            # TODO in application-monitoring/vue repo
            # querystring support for 'se' and 'backend' tags
            
            # TODO in application-monitoring/vue repo
            # Add randomization of failures of Vue app, so can pass it as param in queryString and via TDA here

            # TODO in application-monitoring/vue repo
            # Add "/products", so Home Page can be treated separately. Right now, Home page loads the /produdcts

            # Buttons are not available if products didn't load before selection, so handle this
            try:
                desktop_web_driver.get(endpoint)

                buttonRendered = False
                skips=0
                while buttonRendered==False:
                    try:
                        if skips > 10:
                            sentry_sdk.capture_message("missed button more than 10 skips")
                            buttonRendered=True
                        add_to_cart_btn = desktop_web_driver.find_element(By.CSS_SELECTOR, '.products-list button')
                        for i in range(random.randrange(4) + 1):
                            add_to_cart_btn.click()
                        buttonRendered=True
                    except Exception as err:
                        skips = skips + 1
                        sentry_sdk.capture_message("missed button handling %s skips gracefully" % (skips))
                        time.sleep(1)
                        pass
                # TODO the Vue app class should be .complete-checkout-btn so it matches the React app
                desktop_web_driver.find_element(By.CSS_SELECTOR, '.checkout-button').click()
                time.sleep(random.randrange(2) + 1)

            except Exception as err:
                missedButtons = missedButtons + 1
                sentry_sdk.set_tag("missedButtons", missedButtons)
                sentry_sdk.set_tag("seleniumSessionId", desktop_web_driver.session_id)

                if err:
                    sentry_sdk.capture_exception(err)

            time.sleep(random.randrange(2) + 1)

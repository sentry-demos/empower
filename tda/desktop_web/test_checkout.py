import time
import sentry_sdk
from urllib.parse import urlencode
from conftest import CExp, BACKENDS
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException


PRODUCTS_JOIN_RATIO = 0.5
CEXP_RATIO = 0.3
BYPASS_PREFERRED_BACKENDS_RATIO = 0.6 # backends that have a realistic autofixable error
BYPASS_PREFERRED_BACKENDS = ['flask', 'laravel']

def test_checkout(desktop_web_driver, endpoints, batch_size, backend, random, sleep_length, cexp):
    for endpoint in endpoints.react_endpoints:

        if random.random() < PRODUCTS_JOIN_RATIO:
            endpoint_products = endpoint + "/products?api=join"
        else:
            endpoint_products = endpoint + "/products"

        sentry_sdk.set_tag("endpoint", endpoint_products)
        sentry_sdk.set_tag("batch_size", batch_size)

        for s in range(batch_size):
            url = ""
            
            if random.random() < CEXP_RATIO: # Determine if this iteration should use CExp flow
                current_backend = 'flask'
                ce = cexp()
                sentry_sdk.set_tag("cexp", ce)
            else:
                # For non-CExp flows, use CHECKOUT_FLASK_RATIO probabilities
                ce = None
                probs = {}
                for backend_name in BACKENDS:
                    if backend_name in BYPASS_PREFERRED_BACKENDS:
                        probs[backend_name] = BYPASS_PREFERRED_BACKENDS_RATIO / len(BYPASS_PREFERRED_BACKENDS)
                    else:
                        probs[backend_name] = (1.0 - BYPASS_PREFERRED_BACKENDS_RATIO) / (len(BACKENDS) - len(BYPASS_PREFERRED_BACKENDS))
                    
                
                current_backend = backend(probabilities=probs)
            
            # to generate more flagship errors than Slow DB Query, other performance issues
            checkout_attempts = 1 if ce and ce in [CExp.CHECKOUT_SUCCESS, CExp.ADD_TO_CART_JS_ERROR] else 3

            # TODO make a query_string builder function for sharing this across tests
            query_string = {
                'backend': current_backend,
            }
            if ce:
                query_string['cexp'] = ce

            url = endpoint_products + '?' + urlencode(query_string)
            
            sentry_sdk.metrics.incr(key="test_checkout.iteration.started", value=1, tags=query_string)

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
                    sentry_sdk.metrics.incr(key="test_checkout.iteration.abandoned", value=1, tags=dict(query_string, reason="no_add_to_cart_btn"))
                    continue

                # Add 2 second sleep between the initial /products pageload
                #   and the navigation to the checkout cart
                #   to solve for web vitals issue as transaction may not be resolving
                time.sleep(2)

                for c in range(checkout_attempts):
                    desktop_web_driver.find_element(By.CSS_SELECTOR, '.show-desktop #top-right-links a[href="/cart"]').click()

                    time.sleep(sleep_length())

                    if (ce != CExp.ADD_TO_CART_JS_ERROR):
                        try:
                            desktop_web_driver.find_element(By.CSS_SELECTOR, 'a[href="/checkout"]').click()
                        except NoSuchElementException as err:
                            sentry_sdk.metrics.incr(key="test_checkout.iteration.abandoned", value=1, tags=dict(query_string, reason="no_proceed_to_checkout_btn"))
                            continue

                        time.sleep(sleep_length())
                        
                        desktop_web_driver.find_element(By.CSS_SELECTOR, '#email').send_keys("sampleEmail@email.com")

                        desktop_web_driver.find_element(By.CSS_SELECTOR, '.complete-checkout-btn').click()
                        time.sleep(sleep_length())

                        sentry_sdk.metrics.incr(key="test_checkout.iteration.completed", value=1, tags=query_string)

            except Exception as err:
                sentry_sdk.metrics.incr(key="test_checkout.iteration.abandoned", value=1, tags=dict(query_string, reason=f"other({err.__class__.__name__})"))
                sentry_sdk.capture_exception(err)

            time.sleep(sleep_length())

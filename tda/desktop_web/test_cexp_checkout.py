import time
import sentry_sdk
from urllib.parse import urlencode
from conftest import CExp, BACKENDS, CONFIG
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

# Global counter to track browser runs for promo code
_browser_run_count = 0


# These parameters are picked to create different volume of issues of each type so that the flagship errors
# show up at the top of the Issues feed without being crowded out by less important (from demo POV) issues.
# See: https://github.com/sentry-demos/empower/pull/955
PRODUCTS_JOIN_RATIO = 0.5
CEXP_RATIO = 0.3
BYPASS_PREFERRED_BACKENDS_RATIO = 0.6 # backends that have a realistic autofixable error
BYPASS_PREFERRED_BACKENDS = ['flask', 'laravel']

def test_cexp_checkout(desktop_web_driver, endpoints, batch_size, backend, random, sleep_length, cexp, is_first_run_of_the_day):
    global _browser_run_count
    
    # Increment counter for each browser run
    _browser_run_count += 1
    is_first_browser = _browser_run_count == 1
    
    for endpoint in [endpoints.react_endpoint]:
            
        base_query_string = {}
        endpoint_products = endpoint + "/products"

        if random.random() < PRODUCTS_JOIN_RATIO:
            base_query_string['api'] = 'join'

        sentry_sdk.set_tag("endpoint", endpoint_products)
        sentry_sdk.set_tag("batch_size", batch_size)

        for s in range(batch_size):
            query_string = base_query_string.copy()
            
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


            # Only do for 1 browser (first browser run)
            if is_first_run_of_the_day and is_first_browser:
                apply_promo_code = True
                current_backend = 'flask' # not implemented in other backends
                ce = CExp.CHECKOUT_SUCCESS # avoid getting stuck early in the funnel
                query_string['userEmail']='John.Logs@example.com'
            
            # to generate more flagship errors than Slow DB Query, other performance issues
            checkout_attempts = 1 if ce and ce in [CExp.CHECKOUT_SUCCESS, CExp.ADD_TO_CART_JS_ERROR] else 3

            # TODO make a query_string builder function for sharing this across tests
            query_string['backend'] = current_backend
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

                        # Apply promo code only once per day, only for first browser, only on first checkout attempt
                        if apply_promo_code and c == 0:
                            desktop_web_driver.find_element(By.NAME, 'promoCode').send_keys("SAVE20")
                            desktop_web_driver.find_element(By.NAME, 'applyPromoCode').click()
                            time.sleep(3)

                        desktop_web_driver.find_element(By.CSS_SELECTOR, '.complete-checkout-btn').click()
                        time.sleep(sleep_length())

                        sentry_sdk.metrics.incr(key="test_checkout.iteration.completed", value=1, tags=query_string)

            except Exception as err:
                sentry_sdk.metrics.incr(key="test_checkout.iteration.abandoned", value=1, tags=dict(query_string, reason=f"other({err.__class__.__name__})"))
                sentry_sdk.capture_exception(err)

            time.sleep(sleep_length())

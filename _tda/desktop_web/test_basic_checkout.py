import time
import pytest
import sentry_sdk
from urllib.parse import urlencode
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import (
    ElementClickInterceptedException,
    NoSuchElementException,
    TimeoutException,
)

# Markup rendered by Sentry.showReportDialog(), which the frontends open on purpose
# (e.g. vue/src/main.js beforeSend on "Internal Server Error") as a demo feature.
REPORT_DIALOG_WRAPPER = '.sentry-error-embed-wrapper'
REPORT_DIALOG_CLOSE = '.sentry-error-embed .close'


def dismiss_report_dialog(driver, timeout=5):
    """Close the Sentry user-feedback report dialog if it is covering the page."""
    sentry_sdk.add_breadcrumb(
        category='tda',
        message='Dismissing Sentry report dialog that intercepted a click',
        level='info',
    )
    try:
        driver.find_element(By.CSS_SELECTOR, REPORT_DIALOG_CLOSE).click()
    except Exception:
        # Fall back to removing the overlay so the test can continue interacting with the page
        driver.execute_script(
            "document.querySelectorAll(arguments[0]).forEach(function (el) { el.remove(); });",
            REPORT_DIALOG_WRAPPER,
        )
    try:
        WebDriverWait(driver, timeout).until(
            EC.invisibility_of_element_located((By.CSS_SELECTOR, REPORT_DIALOG_WRAPPER))
        )
    except TimeoutException:
        pass


def click_dismissing_report_dialog(driver, element):
    """Click element; if the Sentry report dialog intercepts it, dismiss the dialog and retry once.

    A second interception propagates so the caller still reports it to Sentry.
    """
    try:
        element.click()
    except ElementClickInterceptedException:
        dismiss_report_dialog(driver)
        element.click()


# Skip before desktop_web_driver so a 0-draw does not open a Sauce session.
@pytest.fixture(autouse=True)
def _skip_if_no_seasonal_volume(unit_seasonal_batch_size):
    if unit_seasonal_batch_size == 0:
        pytest.skip("not running this round — this test fills in when cexp checkout is off-peak")


def test_basic_checkout(desktop_web_driver, endpoints, random, sleep_length, cexp, unit_seasonal_batch_size):
    for endpoint in [endpoints.nextjs_endpoint, endpoints.angular_endpoint, endpoints.vue_endpoint]:

        endpoint_products = endpoint + "/products"

        sentry_sdk.set_tag("endpoint", endpoint_products)
        sentry_sdk.set_tag("batch_size", unit_seasonal_batch_size)

        for b in range(unit_seasonal_batch_size):
            # to generate more flagship errors than Slow DB Query, other performance issues
            checkout_attempts = 3

            query_string = {}
            url = endpoint_products + '?' + urlencode(query_string)
            
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
                        click_dismissing_report_dialog(desktop_web_driver, add_to_cart_btn)
                except NoSuchElementException as err:
                    continue

                # Add 2 second sleep between the initial /products pageload
                #   and the navigation to the checkout cart
                #   to solve for web vitals issue as transaction may not be resolving
                time.sleep(2)

                for c in range(checkout_attempts):
                    desktop_web_driver.find_element(By.CSS_SELECTOR, '.show-desktop #top-right-links a[href="/cart"]').click()

                    time.sleep(sleep_length())

                    try:
                        desktop_web_driver.find_element(By.CSS_SELECTOR, 'a[href="/checkout-form"]').click()
                    except NoSuchElementException as err:
                        continue

                    time.sleep(sleep_length())
                    
                    desktop_web_driver.find_element(By.CSS_SELECTOR, '#email').send_keys("sampleEmail@email.com")

                    desktop_web_driver.find_element(By.CSS_SELECTOR, '.complete-checkout-btn').click()
                    time.sleep(sleep_length())

            except Exception as err:
                sentry_sdk.capture_exception(err)

            time.sleep(sleep_length())

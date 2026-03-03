import time

import sentry_sdk
from appium.webdriver.common.appiumby import AppiumBy


def test_promo_flutter_android(android_flutter_driver, is_first_run_of_the_day):
    if not is_first_run_of_the_day:
        return

    try:
        # ------------------------------------------------------------------
        # Add an item to cart to reach the checkout screen
        # ------------------------------------------------------------------
        android_flutter_driver.find_element(
            AppiumBy.ANDROID_UIAUTOMATOR, 'description("Add to cart")'
        ).click()

        # ------------------------------------------------------------------
        # Navigate to the cart tab, then proceed to checkout
        # ------------------------------------------------------------------
        android_flutter_driver.find_element(
            AppiumBy.ACCESSIBILITY_ID, "Cart\nTab 2 of 2"
        ).click()

        android_flutter_driver.find_element(
            AppiumBy.ACCESSIBILITY_ID, "Proceed to checkout"
        ).click()

        # ------------------------------------------------------------------
        # Apply promo code
        # ------------------------------------------------------------------
        promo_field = android_flutter_driver.find_element(
            AppiumBy.ANDROID_UIAUTOMATOR,
            'className("android.widget.EditText")',
        )
        promo_field.clear()
        promo_field.send_keys("SAVE20")

        android_flutter_driver.find_element(
            AppiumBy.ANDROID_UIAUTOMATOR, 'text("Apply")'
        ).click()

        # Allow time for the promo-code error to be sent to Sentry
        time.sleep(2)

    except Exception as err:
        sentry_sdk.capture_exception(err)

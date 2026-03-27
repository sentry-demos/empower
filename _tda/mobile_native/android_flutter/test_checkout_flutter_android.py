import time

import sentry_sdk
from appium.webdriver.common.appiumby import AppiumBy


def test_checkout_flutter_android(android_flutter_driver):
    try:
        # ------------------------------------------------------------------
        # Add items to cart
        # ------------------------------------------------------------------
        add_to_cart_btn = android_flutter_driver.find_element(
            AppiumBy.ANDROID_UIAUTOMATOR, 'description("Add to cart")'
        )
        add_to_cart_btn.click()
        add_to_cart_btn.click()
        add_to_cart_btn.click()

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
        # Place the order
        # ------------------------------------------------------------------
        android_flutter_driver.find_element(
            AppiumBy.ACCESSIBILITY_ID, "Place your order"
        ).click()

        # ------------------------------------------------------------------
        # User feedback dialog — appears when the checkout request fails.
        # Reduce the implicit wait so we don't block for 20 s on a
        # successful checkout where no dialog is shown.
        # ------------------------------------------------------------------
        android_flutter_driver.implicitly_wait(5)
        try:
            android_flutter_driver.find_element(
                AppiumBy.ANDROID_UIAUTOMATOR,
                'className("android.widget.EditText").instance(0)',
            ).send_keys("John")

            android_flutter_driver.find_element(
                AppiumBy.ANDROID_UIAUTOMATOR,
                'className("android.widget.EditText").instance(1)',
            ).send_keys("Broken")

            android_flutter_driver.find_element(
                AppiumBy.ANDROID_UIAUTOMATOR, 'text("Send")'
            ).click()
        except Exception:
            pass  # Dialog only appears on checkout failure; safe to skip if absent
        finally:
            android_flutter_driver.implicitly_wait(20)

        # Allow time for the checkout transaction and any errors to be sent to Sentry
        time.sleep(5)

    except Exception as err:
        sentry_sdk.capture_exception(err)

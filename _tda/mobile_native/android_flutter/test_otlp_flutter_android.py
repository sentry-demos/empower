import time

import sentry_sdk
from appium.webdriver.common.appiumby import AppiumBy


def test_otlp_flutter_android(android_flutter_driver):
    """OTLP journey: opens the home page but routes all backend calls
    (/products, /checkout) to the OpenTelemetry-instrumented backend
    (flask-otlp), as its own new trace. Exercises both the product fetch and
    a checkout so the trace continues into the OTLP backend.
    """
    try:
        # ------------------------------------------------------------------
        # Open the drawer and start the OTLP journey
        # ------------------------------------------------------------------
        android_flutter_driver.find_element(
            AppiumBy.ACCESSIBILITY_ID, "Open navigation menu"
        ).click()
        android_flutter_driver.find_element(
            AppiumBy.ACCESSIBILITY_ID, "OTLP"
        ).click()

        # The OTLP home now loads products from the flask-otlp backend.
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
        # Navigate to the cart tab, then proceed to checkout (flask-otlp)
        # ------------------------------------------------------------------
        android_flutter_driver.find_element(
            AppiumBy.ACCESSIBILITY_ID, "Cart\nTab 2 of 2"
        ).click()

        android_flutter_driver.find_element(
            AppiumBy.ACCESSIBILITY_ID, "Proceed to checkout"
        ).click()

        # ------------------------------------------------------------------
        # Place the order — POSTs to the OTLP backend's /checkout
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

        # Allow time for the OTLP checkout transaction/trace to be sent to Sentry
        time.sleep(5)

    except Exception as err:
        sentry_sdk.capture_exception(err)

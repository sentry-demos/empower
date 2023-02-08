import time
import sentry_sdk
from appium.webdriver.common.appiumby import AppiumBy

# 'Regular' as in non-react-native
def test_checkout_regular_android(android_emu_driver):
    sentry_sdk.set_tag("pytestName", "test_checkout_regular_android")

    try:
        # Add items to cart
        add_to_cart_btn = android_emu_driver.find_element(AppiumBy.ID, 'com.example.vu.android:id/add_to_cart_btn')
        add_to_cart_btn.click()
        add_to_cart_btn.click()
        add_to_cart_btn.click()
        add_to_cart_btn.click()

        # Checkout button
        android_emu_driver.find_element(AppiumBy.ID, 'com.example.vu.android:id/checkout_btn').click()

        time.sleep(5)

    except Exception as err:
        sentry_sdk.capture_exception(err)
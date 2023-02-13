import time
import sentry_sdk

# 'Regular' as in non-react-native
def test_checkout_regular_android(android_emu_driver):
    sentry_sdk.set_tag("pytestName", "test_checkout_regular_android")

    try:
        # Add items to cart
        add_to_cart_btn = android_emu_driver.find_element_by_id('com.example.vu.android:id/add_to_cart_btn')
        add_to_cart_btn.click()
        add_to_cart_btn.click()
        add_to_cart_btn.click()
        add_to_cart_btn.click()

        # Checkout button
        android_emu_driver.find_element_by_id('com.example.vu.android:id/checkout_btn').click()

    except Exception as err:
        sentry_sdk.capture_exception(err)
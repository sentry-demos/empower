import time
import sentry_sdk
from appium.webdriver.common.appiumby import AppiumBy

def test_checkout_flutter_android(android_flutter_driver):

    try:
        # Add items to cart
        add_to_cart_btn = android_flutter_driver.find_element(AppiumBy.ANDROID_UIAUTOMATOR, 'description("Add to cart")')
        add_to_cart_btn.click()
        add_to_cart_btn.click()
        add_to_cart_btn.click()

        # Checkout button
        android_flutter_driver.find_element(AppiumBy.ACCESSIBILITY_ID, 'Cart\nTab 2 of 2').click()
        
        android_flutter_driver.find_element(AppiumBy.ACCESSIBILITY_ID, 'Proceed to checkout').click()
        
        android_flutter_driver.find_element(AppiumBy.ACCESSIBILITY_ID, 'Place your order').click()

        # Sleep in seconds to allow time for both error and 'checkout' transaction to be sent
        time.sleep(5)

    except Exception as err:
        sentry_sdk.capture_exception(err)
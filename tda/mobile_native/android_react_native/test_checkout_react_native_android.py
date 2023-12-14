import sentry_sdk
from appium.webdriver.common.appiumby import AppiumBy

def test_checkout_react_native_android(android_react_native_emu_driver):

    try:
        add_to_cart_btn = android_react_native_emu_driver.find_element(AppiumBy.XPATH, '(//android.widget.TextView[@text="Add to Cart"])[1]')
        add_to_cart_btn.click()
        add_to_cart_btn.click()
        add_to_cart_btn.click()

        # 'view cart' button
        android_react_native_emu_driver.find_element(AppiumBy.ACCESSIBILITY_ID, 'CART').click()

        # checkout button
        android_react_native_emu_driver.find_element(AppiumBy.ACCESSIBILITY_ID, 'CHECKOUT').click()

        # Appium on android can't find the 'place your order' button
        # unless we scroll down to it
        android_react_native_emu_driver.find_element(AppiumBy.XPATH, '(//android.widget.EditText)[1]')

        top_of_screen_element = android_react_native_emu_driver.find_element(AppiumBy.XPATH, '(//android.widget.EditText)[1]')
        bottom_of_screen_element = android_react_native_emu_driver.find_element(AppiumBy.XPATH, '(//android.widget.EditText)[7]')
        android_react_native_emu_driver.scroll(bottom_of_screen_element, top_of_screen_element)

        # Place order button
        android_react_native_emu_driver.find_element(AppiumBy.XPATH, '//android.widget.TextView[@text="Place your order"]').click()

    except Exception as err:
        sentry_sdk.capture_exception(err)

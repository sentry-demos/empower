import sentry_sdk
from appium.webdriver.common.appiumby import AppiumBy

def test_checkout_react_native_android(android_react_native_emu_driver):

    try:
        add_to_cart_btn = android_react_native_emu_driver.find_element(AppiumBy.XPATH, '(//android.view.ViewGroup[@content-desc="Add to cart"])[1]')
        add_to_cart_btn.click()
        add_to_cart_btn.click()
        add_to_cart_btn.click()

        # Click cart at bottom
        android_react_native_emu_driver.find_element(AppiumBy.XPATH, '//android.widget.TextView[@resource-id="bottom-tab-cart"]').click()

        # checkout button
        android_react_native_emu_driver.find_element(AppiumBy.ACCESSIBILITY_ID, 'CHECKOUT').click()

        # We need to find the elements before the placeholder text is replaced by the demo data
        top_of_screen_element = android_react_native_emu_driver.find_element(AppiumBy.XPATH, '//android.widget.EditText[@text="email"]')
        bottom_of_screen_element = android_react_native_emu_driver.find_element(AppiumBy.XPATH, '//android.widget.EditText[@text="country/region"]')

        # Click to fill in the demo data
        android_react_native_emu_driver.find_element(AppiumBy.XPATH, '//android.widget.EditText[@text="email"]').click()
        if android_react_native_emu_driver.is_keyboard_shown():
            android_react_native_emu_driver.hide_keyboard()

        # Appium on android can't find the 'place your order' button
        # unless we scroll down to it
        android_react_native_emu_driver.scroll(bottom_of_screen_element, top_of_screen_element)

        # Place order button
        android_react_native_emu_driver.find_element(AppiumBy.XPATH, '//android.view.ViewGroup[@content-desc="Place your order"]').click()
        # text element of the button is '//android.widget.TextView[@text="Place your order"]'

    except Exception as err:
        sentry_sdk.capture_exception(err)

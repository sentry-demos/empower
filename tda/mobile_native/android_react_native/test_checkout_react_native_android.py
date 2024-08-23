import sentry_sdk
from appium.webdriver.common.appiumby import AppiumBy

def test_checkout_react_native_android(android_react_native_emu_driver):

    try:
        add_to_cart_btn = android_react_native_emu_driver.find_element(AppiumBy.XPATH, '(//android.view.ViewGroup[@content-desc="Add to cart"])[1]')
        add_to_cart_btn.click()
        add_to_cart_btn.click()
        add_to_cart_btn.click()

        # Click cart at bottom
        android_react_native_emu_driver.find_element(AppiumBy.XPATH, '//android.widget.FrameLayout[@resource-id="android:id/content"]/android.widget.FrameLayout/android.view.ViewGroup/android.view.ViewGroup/android.view.ViewGroup/android.view.ViewGroup[2]/android.view.View/android.view.View[2]').click()

        # checkout button
        android_react_native_emu_driver.find_element(AppiumBy.ACCESSIBILITY_ID, 'CHECKOUT').click()

        android_react_native_emu_driver.find_element(AppiumBy.XPATH, '//android.widget.EditText[@text="email"]').click
        if android_react_native_emu_driver.is_keyboard_shown():
            android_react_native_emu_driver.hide_keyboard()

        # Appium on android can't find the 'place your order' button
        # unless we scroll down to it
        top_of_screen_element = android_react_native_emu_driver.find_element(AppiumBy.XPATH, '//android.widget.EditText[@text="email"]')
        bottom_of_screen_element = android_react_native_emu_driver.find_element(AppiumBy.XPATH, '//android.widget.EditText[@text="country/region"]')
        android_react_native_emu_driver.scroll(bottom_of_screen_element, top_of_screen_element)

        # Place order button
        android_react_native_emu_driver.find_element(AppiumBy.ACCESSIBILITY_ID, 'Place your order').click()

    except Exception as err:
        sentry_sdk.capture_exception(err)

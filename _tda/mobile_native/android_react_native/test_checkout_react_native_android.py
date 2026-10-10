import time
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

        # Click to fill in the demo data
        android_react_native_emu_driver.find_element(AppiumBy.XPATH, '//android.widget.EditText[@text="email"]').click()
        if android_react_native_emu_driver.is_keyboard_shown():
            android_react_native_emu_driver.hide_keyboard()

        # Appium on android can't find the 'Apply' / 'place your order' buttons
        # unless we scroll down to them. Use UiScrollable so the lookup is done
        # against the current screen, instead of holding element references
        # located by placeholder text that the demo data fill replaces
        # (which made them stale and unrecoverable).
        android_react_native_emu_driver.find_element(AppiumBy.ANDROID_UIAUTOMATOR,
            'new UiScrollable(new UiSelector().scrollable(true).instance(0)).scrollIntoView(new UiSelector().description(\"Apply\"))'
        )

        # click 'Apply' promo code button
        android_react_native_emu_driver.find_element(AppiumBy.XPATH, '//android.view.ViewGroup[@content-desc="Apply"]').click()
        time.sleep(3)

        # Place order button
        android_react_native_emu_driver.find_element(AppiumBy.XPATH, '//android.view.ViewGroup[@content-desc="Place your order"]').click()
        # text element of the button is '//android.widget.TextView[@text="Place your order"]'

        # needed for replay to get fully flushed (no missing segments - "Video Unavailable")
        # duration determined empirically for test_checkout
        time.sleep(14) 

    except Exception as err:
        sentry_sdk.capture_exception(err)

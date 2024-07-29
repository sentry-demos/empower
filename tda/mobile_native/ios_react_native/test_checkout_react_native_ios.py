import sentry_sdk
from appium.webdriver.common.appiumby import AppiumBy
import time

def test_checkout_react_native_ios(ios_react_native_sim_driver):

    try:
        cart_btn = ios_react_native_sim_driver.find_element(AppiumBy.XPATH, '(//XCUIElementTypeOther[@name="Add to cart"])[2]')
        cart_btn.click()
        cart_btn.click()
        cart_btn.click()
        cart_btn.click()

        ios_react_native_sim_driver.find_element(AppiumBy.ACCESSIBILITY_ID, 'Cart, tab, 2 of 3').click()
        ios_react_native_sim_driver.find_element(AppiumBy.ACCESSIBILITY_ID, 'Checkout').click()

        ios_react_native_sim_driver.find_element(AppiumBy.XPATH, '//XCUIElementTypeTextField[@value="email"]').click()

        # click 'return' if keyboard is up, as its being shown intermittently
        if ios_react_native_sim_driver.is_keyboard_shown():
            ios_react_native_sim_driver.find_element(AppiumBy.ACCESSIBILITY_ID, 'Return').click()

        ios_react_native_sim_driver.find_element(AppiumBy.XPATH, '(//XCUIElementTypeOther[@name="Place your order"])[2]').click()

    except Exception as err:
        sentry_sdk.capture_exception(err)

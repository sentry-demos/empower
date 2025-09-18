import sentry_sdk
from appium.webdriver.common.appiumby import AppiumBy

def test_captureexception_react_native_ios(ios_react_native_sim_driver):

    try:
        # click on list app
        ios_react_native_sim_driver.find_element(AppiumBy.ACCESSIBILITY_ID, 'Debug, tab, 3 of 3').click()

        # click 'capture exception' button
        btn = ios_react_native_sim_driver.find_element(AppiumBy.ACCESSIBILITY_ID, "Capture Exception")
        btn.click()

    except Exception as err:
        sentry_sdk.capture_exception(err)

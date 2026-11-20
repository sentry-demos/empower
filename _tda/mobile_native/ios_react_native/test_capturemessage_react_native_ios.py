import sentry_sdk
from appium.webdriver.common.appiumby import AppiumBy

def test_capturemessage_react_native_ios(ios_react_native_sim_driver):

    try:
        ios_react_native_sim_driver.find_element(AppiumBy.ACCESSIBILITY_ID, 'landing-enter-button').click()

        # click on list app
        ios_react_native_sim_driver.find_element(AppiumBy.IOS_PREDICATE, "name BEGINSWITH 'Debug, tab,'").click()

        # click 'capture message' button
        btn = ios_react_native_sim_driver.find_element(AppiumBy.ACCESSIBILITY_ID, "Capture Message")
        btn.click()

    except Exception as err:
        sentry_sdk.capture_exception(err)

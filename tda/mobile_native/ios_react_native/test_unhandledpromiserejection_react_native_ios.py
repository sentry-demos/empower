import sentry_sdk
from appium.webdriver.common.appiumby import AppiumBy

def test_unhandledpromiserejection_react_native_ios(ios_react_native_sim_driver):

    try:
        # click on list app
        ios_react_native_sim_driver.find_element(AppiumBy.ACCESSIBILITY_ID, 'Debug, tab, 3 of 3').click()

        # click unhandled promise rejection button
        btn = ios_react_native_sim_driver.find_element(AppiumBy.ACCESSIBILITY_ID, "Unhandled Promise Rejection")
        btn.click()

        time.sleep(2)
    except Exception as err:
        sentry_sdk.capture_exception(err)

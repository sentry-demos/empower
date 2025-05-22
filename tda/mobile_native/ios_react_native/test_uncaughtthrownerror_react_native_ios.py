import time
import sentry_sdk
from appium.webdriver.common.appiumby import AppiumBy

def test_uncaughtthrownerror_react_native_ios(ios_react_native_sim_driver):

    try:
        # click on list app
        ios_react_native_sim_driver.find_element(AppiumBy.ACCESSIBILITY_ID, 'Debug, tab, 3 of 3').click()

        # click uncaught-error button
        btn = ios_react_native_sim_driver.find_element(AppiumBy.ACCESSIBILITY_ID, "Uncaught Thrown Error")
        btn.click()

        time.sleep(6)
        ios_react_native_sim_driver.close_app() # in case hasn't crashed 
        ios_react_native_sim_driver.launch_app() # we don't send replay segments upon crash to avoid blocking
        time.sleep(6)

    except Exception as err:
        sentry_sdk.capture_exception(err)

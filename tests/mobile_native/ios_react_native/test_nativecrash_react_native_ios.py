import sentry_sdk
from appium.webdriver.common.appiumby import AppiumBy

def test_nativecrash_react_native_ios(ios_react_native_sim_driver):
    sentry_sdk.set_tag("pytestName", "test_nativecrash_react_native_ios")

    try:
        # click on list app
        ios_react_native_sim_driver.find_element(AppiumBy.XPATH, '//XCUIElementTypeButton[@name="List App"]').click()
        
        # click 'native crash' button
        btn = ios_react_native_sim_driver.find_element(AppiumBy.ACCESSIBILITY_ID, "Native Crash")
        btn.click()
        # launch app again or the error does not get sent to Sentry
        ios_react_native_sim_driver.launch_app()
    
    except Exception as err:
        sentry_sdk.capture_exception(err)
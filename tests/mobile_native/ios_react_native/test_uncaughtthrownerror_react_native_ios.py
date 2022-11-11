import sentry_sdk

def test_uncaughtthrownerror_react_native_ios(ios_react_native_sim_driver):
    sentry_sdk.set_tag("pytestName", "test_uncaughtthrownerror_react_native_ios")
    
    try:
        # click on list app
        ios_react_native_sim_driver.find_element_by_xpath('//XCUIElementTypeButton[@name="List App"]').click()
        
        # click uncaught-error button
        btn = ios_react_native_sim_driver.find_element_by_accessibility_id("Uncaught Thrown Error")
        btn.click()
        # launch app again or the error does not get sent to Sentry
        ios_react_native_sim_driver.launch_app()
    
    except Exception as err:
        sentry_sdk.capture_exception(err)

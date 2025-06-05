import sentry_sdk
import time
from appium.webdriver.common.appiumby import AppiumBy

def test_error_list_ios(ios_sim_driver):

    try:
        ios_sim_driver.find_element(AppiumBy.ACCESSIBILITY_ID, "more").click()
        ios_sim_driver.find_element(AppiumBy.XPATH, '//XCUIElementTypeStaticText[@name="Error"]').click()
        ios_sim_driver.find_element(AppiumBy.XPATH, '//XCUIElementTypeStaticText[@name="NSException"]').click()
        ios_sim_driver.find_element(AppiumBy.XPATH, '//XCUIElementTypeStaticText[@name="Fatal Error"]').click()
        ios_sim_driver.activate_app('sentrydemos.ios.EmpowerPlant')

        ios_sim_driver.find_element(AppiumBy.ACCESSIBILITY_ID, "more").click()
        ios_sim_driver.find_element(AppiumBy.XPATH, '//XCUIElementTypeStaticText[@name="ANR Fully Blocking"]').click()
        ios_sim_driver.activate_app('sentrydemos.ios.EmpowerPlant')

        ios_sim_driver.find_element(AppiumBy.ACCESSIBILITY_ID, "more").click()
        ios_sim_driver.find_element(AppiumBy.XPATH, '//XCUIElementTypeStaticText[@name="ANR Filling Run Loop"]').click()
        ios_sim_driver.activate_app('sentrydemos.ios.EmpowerPlant')
        
        time.sleep(5)
        # wait for confirmation of purchase? (currently nothing happens)

    except Exception as err:
        # sentry_sdk.capture_exception(err)
        raise err

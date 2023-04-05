import sentry_sdk
import time
from appium.webdriver.common.appiumby import AppiumBy

def test_errorlist_ios(ios_sim_driver):

    try:
        ios_sim_driver.find_element(AppiumBy.ACCESSIBILITY_ID, "more").click()
        ios_sim_driver.find_element(AppiumBy.XPATH, '//XCUIElementTypeStaticText[@name="Error"]').click()
        ios_sim_driver.find_element(AppiumBy.XPATH, '//XCUIElementTypeStaticText[@name="NSException"]').click()
        ios_sim_driver.find_element(AppiumBy.XPATH, '//XCUIElementTypeStaticText[@name="Fatal Error"]').click()
        # time.sleep(5)
        ios_sim_driver.launch_app()

        ios_sim_driver.find_element(AppiumBy.ACCESSIBILITY_ID, "more").click()
        ios_sim_driver.find_element(AppiumBy.XPATH, '//XCUIElementTypeStaticText[@name="DiskWriteException (!)"]').click()
        ios_sim_driver.find_element(AppiumBy.XPATH, '//XCUIElementTypeStaticText[@name="HighCPULoad"]').click()
        ios_sim_driver.find_element(AppiumBy.XPATH, '//XCUIElementTypeStaticText[@name="Permissions (!)"]').click()
        ios_sim_driver.find_element(AppiumBy.XPATH, '//XCUIElementTypeStaticText[@name="Async Crash (!)"]').click()
        # time.sleep(5)
        ios_sim_driver.launch_app()

        ios_sim_driver.find_element(AppiumBy.ACCESSIBILITY_ID, "more").click()
        ios_sim_driver.find_element(AppiumBy.XPATH, '//XCUIElementTypeStaticText[@name="ANR Fully Blocking"]').click()
        # time.sleep(5)
        ios_sim_driver.launch_app()

        ios_sim_driver.find_element(AppiumBy.ACCESSIBILITY_ID, "more").click()
        ios_sim_driver.find_element(AppiumBy.XPATH, '//XCUIElementTypeStaticText[@name="ANR Filling Run Loop"]').click()

        # time.sleep(5)
        ios_sim_driver.launch_app()
        # time.sleep(5)

        # wait for confirmation of purchase? (currently nothing happens)

    except Exception as err:
        # sentry_sdk.capture_exception(err)
        raise err

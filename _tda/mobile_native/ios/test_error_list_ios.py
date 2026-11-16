import sentry_sdk
import time
from appium.webdriver.common.appiumby import AppiumBy
from conftest import ios_tap

BUNDLE_ID = "sentrydemos.ios.EmpowerPlant"


# Crash reports are sent on the next launch
def relaunch(driver):
    time.sleep(4)  # crash rows flush for up to 2s before crashing
    driver.terminate_app(BUNDLE_ID)
    driver.activate_app(BUNDLE_ID)
    driver.find_element(AppiumBy.ACCESSIBILITY_ID, "more")  # SDK has started and queued the report
    time.sleep(10)


def test_error_list_ios(ios_sim_driver):

    try:
        ios_tap(ios_sim_driver, "more")
        # Its toast dims the screen for 5s and swallows taps
        ios_tap(ios_sim_driver, "Error", wait=6)
        ios_tap(ios_sim_driver, "NSException")
        ios_tap(ios_sim_driver, "DiskWriteException (!)")
        ios_tap(ios_sim_driver, "Permissions (!)")
        ios_tap(ios_sim_driver, "File I/O on Main Thread", wait=5)
        ios_tap(ios_sim_driver, "ANR Fully Blocking", wait=8)
        ios_tap(ios_sim_driver, "ANR Filling Run Loop", wait=8)
        ios_tap(ios_sim_driver, "HighCPULoad", wait=3)
        ios_tap(ios_sim_driver, "Fatal Error")
        relaunch(ios_sim_driver)

        ios_tap(ios_sim_driver, "more")
        ios_tap(ios_sim_driver, "Async Crash (!)")
        relaunch(ios_sim_driver)

        ios_tap(ios_sim_driver, "ProductCell_Botana Voice")
        ios_tap(ios_sim_driver, "WaterPlant", wait=5)
        ios_tap(ios_sim_driver, "RepotPlant")
        relaunch(ios_sim_driver)

    except Exception as err:
        sentry_sdk.capture_exception(err)
        raise err

import sentry_sdk
import time
from appium.webdriver.common.appiumby import AppiumBy

BUNDLE_ID = "sentrydemos.ios.EmpowerPlant"

# Must match driver.implicitly_wait() in conftest.py ios_sim_driver
DEFAULT_IMPLICIT_WAIT = 20
OPTIONAL_ROW_WAIT = 3

# Lets a crash or main-thread freeze finish before the app is terminated
SETTLE_SECONDS = 6
# Crash reports are sent on the next launch
UPLOAD_WAIT_SECONDS = 5


def row_xpath(title):
    return f'//XCUIElementTypeStaticText[@name="{title}"]'


def open_other_issues(driver):
    driver.find_element(AppiumBy.ACCESSIBILITY_ID, "more").click()


def tap_row(driver, title):
    driver.find_element(AppiumBy.XPATH, row_xpath(title)).click()


# Rows marked (!) exist only in newer app builds (not in 0.0.44)
def tap_row_if_present(driver, title):
    driver.implicitly_wait(OPTIONAL_ROW_WAIT)
    try:
        rows = driver.find_elements(AppiumBy.XPATH, row_xpath(title))
    finally:
        driver.implicitly_wait(DEFAULT_IMPLICIT_WAIT)
    if not rows:
        print(f"Skipping '{title}': not in this app build")
        return
    rows[0].click()


def relaunch(driver):
    time.sleep(SETTLE_SECONDS)
    driver.terminate_app(BUNDLE_ID)
    driver.activate_app(BUNDLE_ID)
    time.sleep(UPLOAD_WAIT_SECONDS)
    open_other_issues(driver)


def test_error_list_ios(ios_sim_driver):

    try:
        open_other_issues(ios_sim_driver)
        tap_row(ios_sim_driver, "Error")
        tap_row(ios_sim_driver, "NSException")
        tap_row(ios_sim_driver, "Fatal Error")
        relaunch(ios_sim_driver)

        tap_row_if_present(ios_sim_driver, "DiskWriteException (!)")
        tap_row(ios_sim_driver, "HighCPULoad")
        tap_row_if_present(ios_sim_driver, "Permissions (!)")
        tap_row_if_present(ios_sim_driver, "Async Crash (!)")
        relaunch(ios_sim_driver)

        tap_row(ios_sim_driver, "ANR Fully Blocking")
        relaunch(ios_sim_driver)

        tap_row(ios_sim_driver, "ANR Filling Run Loop")
        relaunch(ios_sim_driver)

    except Exception as err:
        sentry_sdk.capture_exception(err)
        raise err

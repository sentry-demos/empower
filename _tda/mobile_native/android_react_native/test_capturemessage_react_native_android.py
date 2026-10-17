import time
import sentry_sdk
from appium.webdriver.common.appiumby import AppiumBy
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

# Stable locator for the Debug (list app) tab, same accessibility label used by the iOS RN tests.
DEBUG_TAB = (AppiumBy.ACCESSIBILITY_ID, 'Debug, tab, 3 of 3')
# Legacy fallback: first icon-font glyph TextView (ambiguous, only used if the label above is absent).
DEBUG_TAB_FALLBACK = (AppiumBy.XPATH, '//android.widget.TextView[@text=""]')
CAPTURE_MESSAGE_BTN = (AppiumBy.XPATH, '//android.widget.TextView[@text="Capture Message"]')


def _open_debug_tab(driver, timeout=20):
    """Wait for the Debug tab to be tappable and tap it."""
    try:
        WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(DEBUG_TAB)).click()
    except TimeoutException:
        WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(DEBUG_TAB_FALLBACK)).click()


def _wait_for_capture_message(driver, timeout):
    return WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(CAPTURE_MESSAGE_BTN))


def test_capturemessage_react_native_android(android_react_native_emu_driver):
    driver = android_react_native_emu_driver

    try:
        driver.find_element(AppiumBy.XPATH, '//android.view.ViewGroup[@content-desc="Shop Now"]').click()

        # explicit waits below; disable implicit wait so polling timeouts are accurate
        driver.implicitly_wait(0)

        # click into list app screen, and verify navigation actually happened (retry tap once)
        _open_debug_tab(driver)
        try:
            btn = _wait_for_capture_message(driver, 10)
        except TimeoutException:
            _open_debug_tab(driver)
            btn = _wait_for_capture_message(driver, 20)

        # trigger message
        btn.click()

        time.sleep(2) # sufficient for error + replay to go through > 90% of the time

    except Exception as err:
        sentry_sdk.capture_exception(err)

from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

SHOP_NOW = (AppiumBy.XPATH, '//android.view.ViewGroup[@content-desc="Shop Now"]')
GEAR_TAB = (AppiumBy.XPATH, '//android.widget.TextView[@text="\uf013"]')

# implicit wait configured by android_react_native_emu_driver fixture in conftest.py
DEFAULT_IMPLICIT_WAIT = 20


def rn_android_open_debug_tab(driver, timeout=60):
    """Wait for the React Native app to be ready, dismiss the landing screen
    if shown, then open the gear (Debug/list app) tab.

    The fixture uses appWaitForLaunch=False, so on a cold Sauce emulator the
    app may not be in the foreground yet when the test starts.
    """
    # Disable implicit wait so it doesn't stack with the explicit waits below
    driver.implicitly_wait(0)
    try:
        wait = WebDriverWait(driver, timeout)
        wait.until(EC.any_of(
            EC.presence_of_element_located(SHOP_NOW),
            EC.presence_of_element_located(GEAR_TAB),
        ))

        shop_now = driver.find_elements(*SHOP_NOW)
        if shop_now:
            shop_now[0].click()

        wait.until(EC.element_to_be_clickable(GEAR_TAB)).click()
    finally:
        driver.implicitly_wait(DEFAULT_IMPLICIT_WAIT)

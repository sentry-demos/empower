import time
import sentry_sdk
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def test_nativecrash_react_native_android(android_react_native_emu_driver):

    try:
        driver = android_react_native_emu_driver

        # Wait up to 60s for the app to fully launch before interacting
        WebDriverWait(driver, 60).until(
            EC.presence_of_element_located((AppiumBy.XPATH, '//android.view.ViewGroup[@content-desc="Shop Now"]'))
        ).click()

        # click into list app screen
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((AppiumBy.XPATH, '//android.widget.TextView[@text="\uf013"]'))
        ).click()

        # trigger crash
        btn = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((AppiumBy.XPATH, '//android.widget.TextView[@text="Native Crash"]'))
        )
        btn.click()

        # launch app again or the error does not get sent to Sentry
        driver.launch_app()

        time.sleep(5) # success rate is ~ 46% regardless of sleep duration (must be at least 2 seconds)

    except Exception as err:
        sentry_sdk.capture_exception(err)

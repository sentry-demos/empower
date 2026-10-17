import time
import sentry_sdk
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def test_capturemessage_react_native_android(android_react_native_emu_driver):

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

        # trigger message
        btn = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((AppiumBy.XPATH, '//android.widget.TextView[@text="Capture Message"]'))
        )
        btn.click()

        time.sleep(2) # sufficient for error + replay to go through > 90% of the time

    except Exception as err:
        sentry_sdk.capture_exception(err)

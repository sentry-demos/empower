import time
import sentry_sdk
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def test_uncaughtthrownerror_react_native_android(android_react_native_emu_driver):

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

        # trigger error
        btn = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((AppiumBy.XPATH, '//android.widget.TextView[@text="Uncaught Thrown Error"]'))
        )
        btn.click()

        # launch app again or the error does not get sent to Sentry
        # still ~ 83% success rate
        driver.launch_app()

        time.sleep(10) # replay success rate is ~ 75% for sleep >= 10 seconds and ~ 50% for sleep = 5 seconds

    except Exception as err:
        sentry_sdk.capture_exception(err)

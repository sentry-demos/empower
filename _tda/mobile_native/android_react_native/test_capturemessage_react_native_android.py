import time
import sentry_sdk
from appium.webdriver.common.appiumby import AppiumBy

def test_capturemessage_react_native_android(android_react_native_emu_driver):

    try:
        # click into list app screen
        android_react_native_emu_driver.find_element(AppiumBy.XPATH, '//android.widget.TextView[@text=""]').click()

        # trigger message
        btn = android_react_native_emu_driver.find_element(AppiumBy.XPATH, '//android.widget.TextView[@text="Capture Message"]')
        btn.click()
        
        time.sleep(2) # sufficient for error + replay to go through > 90% of the time

    except Exception as err:
        sentry_sdk.capture_exception(err)

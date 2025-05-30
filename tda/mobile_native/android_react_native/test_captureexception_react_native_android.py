import time
import sentry_sdk
from appium.webdriver.common.appiumby import AppiumBy

def test_captureexception_react_native_android(android_react_native_emu_driver):

    try:
        # click into list app screen
        android_react_native_emu_driver.find_element(AppiumBy.XPATH, '//android.widget.TextView[@text=""]').click()

        # trigger exception
        btn = android_react_native_emu_driver.find_element(AppiumBy.XPATH, '//android.widget.TextView[@text="Capture Exception"]')
        btn.click()
        
        # needed for error to go through as well (likely shorter duration than required for replay)
        time.sleep(14) # needed for replay to get flushed, duration determined empirically for test_checkout

    except Exception as err:
        sentry_sdk.capture_exception(err)

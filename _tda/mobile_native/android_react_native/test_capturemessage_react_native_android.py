import time
import sentry_sdk
from appium.webdriver.common.appiumby import AppiumBy
from rn_android_helpers import rn_android_open_debug_tab

def test_capturemessage_react_native_android(android_react_native_emu_driver):

    try:
        # wait for app, dismiss landing screen, click into list app screen
        rn_android_open_debug_tab(android_react_native_emu_driver)

        # trigger message
        btn = android_react_native_emu_driver.find_element(AppiumBy.XPATH, '//android.widget.TextView[@text="Capture Message"]')
        btn.click()
        
        time.sleep(2) # sufficient for error + replay to go through > 90% of the time

    except Exception as err:
        sentry_sdk.capture_exception(err)

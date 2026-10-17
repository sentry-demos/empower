import time
import sentry_sdk
from appium.webdriver.common.appiumby import AppiumBy
from rn_android_helpers import rn_android_open_debug_tab

def test_nativecrash_react_native_android(android_react_native_emu_driver):

    try:
        # wait for app, dismiss landing screen, click into list app screen
        rn_android_open_debug_tab(android_react_native_emu_driver)

        # trigger crash
        btn = android_react_native_emu_driver.find_element(AppiumBy.XPATH, '//android.widget.TextView[@text="Native Crash"]')
        btn.click()

        # launch app again or the error does not get sent to Sentry
        android_react_native_emu_driver.launch_app()

        time.sleep(5) # success rate is ~ 46% regardless of sleep duration (must be at least 2 seconds)

    except Exception as err:
        sentry_sdk.capture_exception(err)

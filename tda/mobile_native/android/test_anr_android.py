import time
import pytest
import subprocess
import sentry_sdk
from appium.webdriver.common.appiumby import AppiumBy

# Application Not Responding button
def test_anr_android(android_emu_driver):

    try:
        # navigate to list app
        android_emu_driver.find_element(AppiumBy.ACCESSIBILITY_ID, 'More').click()
        android_emu_driver.find_element(AppiumBy.ID, 'com.example.vu.android:id/content').click()

        # trigger error
        android_emu_driver.find_element(AppiumBy.ID, 'com.example.vu.android:id/anr').click()

        # keep clicking on the button for a while so the ANR is thrown with "Input dispatching timeout"
        # we can't use Appium's driver here as it's also locked together with the ANR, so we send taps directly via adb
        time.sleep(1)
        subprocess.run(["adb", "shell", "input", "tap", "200", "200"])
        
        time.sleep(1)
        subprocess.run(["adb", "shell", "input", "tap", "200", "200"])

        # Click "Close app" in the ANR dialog
        android_emu_driver.find_element(AppiumBy.ID, 'android:id/aerr_close').click()

        # Give system some time to recover
        time.sleep(2)

        android_emu_driver.execute_script('mobile: startActivity', {
            'component': 'com.example.vu.android/.empowerplant.EmpowerPlantActivity',
            'action': 'android.intent.action.MAIN',
            'extras': [['z', 'relaunch_for_send', 'true']]
        })

        # sleep after relaunch to make sure error (+ traces + replays) makes it to the server
        time.sleep(8)
    except Exception as err:
        sentry_sdk.capture_exception(err)
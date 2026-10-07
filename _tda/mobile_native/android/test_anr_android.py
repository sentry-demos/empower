import time
import pytest
import subprocess
import sentry_sdk
from appium.webdriver.common.appiumby import AppiumBy
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException

ANR_CLOSE_BUTTON_ID = 'android:id/aerr_close'
APP_PACKAGE = 'com.example.vu.android'


def dismiss_anr_dialog(driver, timeout=10, interval=0.5):
    """Click 'Close app' on the system ANR dialog, re-locating the element on every attempt.

    The ANR dialog is owned by system_server and may be re-rendered or dismissed at any time,
    so a previously found element reference can go stale before the click is delivered.
    Returns True if the click succeeded, False if the dialog could not be clicked in time.
    """
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            driver.find_element(AppiumBy.ID, ANR_CLOSE_BUTTON_ID).click()
            return True
        except (StaleElementReferenceException, NoSuchElementException):
            time.sleep(interval)
    return False


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
        try:
            time.sleep(1)
            android_emu_driver.execute_script('mobile: shell', {
                'command': 'input',
                'args': ['tap', '200', '200'],
                'timeout': 5000
            })
        except Exception:
            pass # it's expected to fail but it's still gonna click and cause an ANR     
            
        try:
            time.sleep(1)
            android_emu_driver.execute_script('mobile: shell', {
                'command': 'input',
                'args': ['tap', '200', '200'],
                'timeout': 5000
            })
        except Exception:
            pass # it's expected to fail but it's still gonna click and cause an ANR

        # Click "Close app" in the ANR dialog
        if not dismiss_anr_dialog(android_emu_driver):
            # Dialog vanished before we could click it; make sure the frozen app is killed
            # so the ANR gets reported on relaunch.
            android_emu_driver.execute_script('mobile: shell', {
                'command': 'am',
                'args': ['force-stop', APP_PACKAGE],
            })

        # Give system some time to recover
        time.sleep(3)

        android_emu_driver.execute_script('mobile: startActivity', {
            'component': 'com.example.vu.android/.empowerplant.EmpowerPlantActivity',
            'action': 'android.intent.action.MAIN',
            'extras': [['z', 'relaunch_for_send', 'true']]
        })

        # sleep after relaunch to make sure error (+ traces + replays) makes it to the server
        time.sleep(8)
    except Exception as err:
        sentry_sdk.capture_exception(err)
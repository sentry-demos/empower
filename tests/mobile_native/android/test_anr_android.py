import time
import pytest
import sentry_sdk
from appium.webdriver.common.appiumby import AppiumBy

# Application Not Responding button
@pytest.mark.skip(reason="not working")
def test_anr_android(android_emu_driver):

    try:
        # navigate to list app
        android_emu_driver.find_element(AppiumBy.ACCESSIBILITY_ID, 'More').click()
        android_emu_driver.find_element(AppiumBy.XPATH, '/hierarchy/android.widget.FrameLayout/android.widget.FrameLayout/android.widget.ListView/android.widget.LinearLayout/android.widget.LinearLayout').click()

        # trigger error
        btn = android_emu_driver.find_element(AppiumBy.XPATH, '/hierarchy/android.widget.FrameLayout/android.widget.LinearLayout/android.widget.FrameLayout/android.view.ViewGroup/android.widget.FrameLayout[2]/android.widget.LinearLayout/android.widget.ScrollView/android.widget.LinearLayout/android.widget.Button[4]')
        btn.click()

        # TODO get the event to send to Sentry.io
        time.sleep(10)
        android_emu_driver.launch_app()

    except Exception as err:
        sentry_sdk.capture_exception(err)
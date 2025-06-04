import time
import sentry_sdk
from appium.webdriver.common.appiumby import AppiumBy

# NDK/C++ Native Crash SIGSEGV button
def test_nativecrash_android(android_emu_driver):

    try:
        # navigate to list app
        android_emu_driver.find_element(AppiumBy.ACCESSIBILITY_ID, 'More').click()
        android_emu_driver.find_element(AppiumBy.ID, 'com.example.vu.android:id/content').click()

        # swipe down to have the Native Crash button in the frame
        android_emu_driver.find_element(AppiumBy.ANDROID_UIAUTOMATOR,
            'new UiScrollable(new UiSelector().scrollable(true).instance(0)).scrollIntoView(new UiSelector().resourceId(\"com.example.vu.android:id/native_crash\"))'
        )

        # nativecrash button
        android_emu_driver.find_element(AppiumBy.ID, 'com.example.vu.android:id/native_crash').click()

        android_emu_driver.execute_script('mobile: startActivity', {
            'component': 'com.example.vu.android/.empowerplant.EmpowerPlantActivity',
            'action': 'android.intent.action.MAIN',
            'extras': [['z', 'relaunch_for_send', 'true']]
        })

        # sleep after relaunch to make sure error (+ traces + replays) makes it to the server
        time.sleep(8)

    except Exception as err:
        sentry_sdk.capture_exception(err)
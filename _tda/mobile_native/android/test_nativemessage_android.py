import time
import sentry_sdk
from appium.webdriver.common.appiumby import AppiumBy

# NDK/C++ Native Message button
def test_nativemessage_android(android_emu_driver):

    try:
        # navigate to list app
        android_emu_driver.find_element(AppiumBy.ACCESSIBILITY_ID, 'More').click()
        android_emu_driver.find_element(AppiumBy.ID, 'com.example.vu.android:id/content').click()

        # swipe down to have the Native Message button in the frame
        android_emu_driver.find_element(AppiumBy.ANDROID_UIAUTOMATOR,
            'new UiScrollable(new UiSelector().scrollable(true).instance(0)).scrollIntoView(new UiSelector().resourceId(\"com.example.vu.android:id/native_message\"))'
        )

        # nativemessage button
        android_emu_driver.find_element(AppiumBy.ID, 'com.example.vu.android:id/native_message').click()
        
        time.sleep(4)
    except Exception as err:
        sentry_sdk.capture_exception(err)
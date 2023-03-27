import sentry_sdk
from appium.webdriver.common.appiumby import AppiumBy

# NDK/C++ Native Message button
def test_nativemessage_android(android_emu_driver):

    try:
        # navigate to list app
        android_emu_driver.find_element(AppiumBy.ACCESSIBILITY_ID, 'More').click()
        android_emu_driver.find_element(AppiumBy.ID, 'com.example.vu.android:id/content').click()

        # swipe down to have the Native Message button in the frame
        android_emu_driver.swipe(start_x=0, start_y=1100, end_x=0, end_y=500, duration=800)

        # nativemessage button
        android_emu_driver.find_element(AppiumBy.ID, 'com.example.vu.android:id/native_message').click()
        
    except Exception as err:
        sentry_sdk.capture_exception(err)
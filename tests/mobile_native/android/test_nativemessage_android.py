import sentry_sdk

# NDK/C++ Native Message button
def test_nativemessage_android(android_emu_driver):
    sentry_sdk.set_tag("pytestName", "test_nativemessage_android")

    try:
        # navigate to list app
        android_emu_driver.find_element_by_accessibility_id('More').click()
        android_emu_driver.find_element_by_id('com.example.vu.android:id/content').click()

        # swipe down to have the Native Message button in the frame
        android_emu_driver.swipe(start_x=0, start_y=1100, end_x=0, end_y=500, duration=800)

        # nativemessage button
        android_emu_driver.find_element_by_id('com.example.vu.android:id/native_message').click()
        
    except Exception as err:
        sentry_sdk.capture_exception(err)
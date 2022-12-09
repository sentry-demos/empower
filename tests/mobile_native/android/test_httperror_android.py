import time
import sentry_sdk

# Automatically capture HTTP Errors with range (400 - 599) status codes
def test_httperror_android(android_emu_driver):
    sentry_sdk.set_tag("pytestName", "test_httperror_android")

    try:
        # navigate to list app
        android_emu_driver.find_element_by_accessibility_id('More').click()
        android_emu_driver.find_element_by_xpath('/hierarchy/android.widget.FrameLayout/android.widget.FrameLayout/android.widget.ListView/android.widget.LinearLayout/android.widget.LinearLayout').click()

        # swipe down to have the HTTP Error button in the frame
        android_emu_driver.swipe(start_x=0, start_y=1100, end_x=0, end_y=500, duration=800)
        # HTTP Error button
        android_emu_driver.find_element_by_id('com.example.vu.android:id/error_404').click()

    except Exception as err:
        sentry_sdk.capture_exception(err)
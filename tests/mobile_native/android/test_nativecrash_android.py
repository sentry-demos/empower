import time
import pytest
# NDK/C++ Native Crash SIGSEGV button
@pytest.mark.skip(reason="not working")
def test_nativecrash_android(android_emu_driver):
    btn = android_emu_driver.find_element_by_xpath('/hierarchy/android.widget.FrameLayout/android.widget.LinearLayout/android.widget.FrameLayout/android.view.ViewGroup/android.widget.FrameLayout[2]/android.widget.LinearLayout/android.widget.ScrollView/android.widget.LinearLayout/android.widget.Button[4]')
    btn.click()

    # TODO get the event to send to Sentry.io
    time.sleep(5)
    android_emu_driver.launch_app()
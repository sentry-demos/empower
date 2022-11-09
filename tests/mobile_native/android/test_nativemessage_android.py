import sentry_sdk

# NDK/C++ Native Message button
def test_nativemessage_android(android_emu_driver):
    sentry_sdk.set_tag("pytestName", "test_nativemessage_android")

    try:
        # navigate to list app
        android_emu_driver.find_element_by_accessibility_id('More').click()
        android_emu_driver.find_element_by_xpath('/hierarchy/android.widget.FrameLayout/android.widget.FrameLayout/android.widget.ListView/android.widget.LinearLayout/android.widget.LinearLayout').click()

        # scroll down first, so the nativemessage button can become visible
        bottom_of_screen_element = android_emu_driver.find_element_by_xpath('/hierarchy/android.widget.FrameLayout/android.widget.LinearLayout/android.widget.FrameLayout/android.view.ViewGroup/android.widget.FrameLayout[2]/android.widget.LinearLayout/android.widget.ScrollView/android.widget.LinearLayout/android.widget.Button[4]')
        top_of_screen_element = android_emu_driver.find_element_by_xpath('/hierarchy/android.widget.FrameLayout/android.widget.LinearLayout/android.widget.FrameLayout/android.view.ViewGroup/android.widget.FrameLayout[2]/android.widget.LinearLayout/android.widget.ScrollView/android.widget.LinearLayout/android.widget.Button[1]')
        android_emu_driver.scroll(bottom_of_screen_element, top_of_screen_element)

        # nativemessage button
        btn = android_emu_driver.find_element_by_xpath('/hierarchy/android.widget.FrameLayout/android.widget.LinearLayout/android.widget.FrameLayout/android.view.ViewGroup/android.widget.FrameLayout[2]/android.widget.LinearLayout/android.widget.ScrollView/android.widget.LinearLayout/android.widget.Button[5]')
        btn.click()
        
    except Exception as err:
        sentry_sdk.capture_exception(err)
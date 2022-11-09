import sentry_sdk

# Clicks the Handled Error button that says ArrayIndexOutOfBoundsException
def test_handlederror_android(android_emu_driver):
    sentry_sdk.set_tag("pytestName", "test_handlederror_android")

    try:
        # navigate to list app
        android_emu_driver.find_element_by_accessibility_id('More').click()
        android_emu_driver.find_element_by_xpath('/hierarchy/android.widget.FrameLayout/android.widget.FrameLayout/android.widget.ListView/android.widget.LinearLayout/android.widget.LinearLayout').click()

        # trigger error
        btn = android_emu_driver.find_element_by_xpath('/hierarchy/android.widget.FrameLayout/android.widget.LinearLayout/android.widget.FrameLayout/android.view.ViewGroup/android.widget.FrameLayout[2]/android.widget.LinearLayout/android.widget.ScrollView/android.widget.LinearLayout/android.widget.Button[3]')
        btn.click()
        
    except Exception as err:
        sentry_sdk.capture_exception(err)
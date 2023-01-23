import sentry_sdk

# Clicks the Handled Error button that says ArrayIndexOutOfBoundsException
def test_handlederror_android(android_emu_driver):
    sentry_sdk.set_tag("pytestName", "test_handlederror_android")

    try:
        # navigate to list app
        android_emu_driver.find_element_by_accessibility_id('More').click()
        android_emu_driver.find_element_by_id('com.example.vu.android:id/content').click()

        # trigger error
        btn = android_emu_driver.find_element_by_id('com.example.vu.android:id/handled_exception')
        btn.click()
        
    except Exception as err:
        sentry_sdk.capture_exception(err)
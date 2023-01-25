import sentry_sdk

# Clicks the Unhandled Error button that says ArithmeticException
def test_unhandlederror_android(android_emu_driver):
    sentry_sdk.set_tag("pytestName", "test_unhandlederror_android")

    try:
        # navigate to list app
        android_emu_driver.find_element_by_accessibility_id('More').click()
        android_emu_driver.find_element_by_id('com.example.vu.android:id/content').click()

        sentry_sdk.add_breadcrumb(
            category='btn.click',
            message='navigated to list app via accessibility_id and xpath elements',
            level='info',
        )

        # trigger error
        android_emu_driver.find_element_by_id('com.example.vu.android:id/div_zero').click()

        sentry_sdk.add_breadcrumb(
            category='btn.click',
            message='clicked button via xpath',
            level='info',
        )
        
        android_emu_driver.launch_app()
    
    except Exception as err:
        sentry_sdk.capture_exception(err)
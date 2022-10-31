import sentry_sdk

# Clicks the Unhandled Error button that says ArithmeticException
def test_unhandlederror_android(android_emu_driver):
    sentry_sdk.capture_message("running test_unhandlederror_android")

    sentry_sdk.set_tag("pytestName", "test_unhandlederror_android")
    # TODO target | device | platform or parse it out of pytestName

    try:
        # navigate to list app
        android_emu_driver.find_element_by_accessibility_id('More').click()
        android_emu_driver.find_element_by_xpath('/hierarchy/android.widget.FrameLayout/android.widget.FrameLayout/android.widget.ListView/android.widget.LinearLayout/android.widget.LinearLayout').click()

        sentry_sdk.add_breadcrumb(
            category='btn.click',
            message='navigated to list app via accessibility_id and xpath elements',
            level='info',
        )

        # trigger error
        btn = android_emu_driver.find_element_by_xpath('/hierarchy/android.widget.FrameLayout/android.widget.LinearLayout/android.widget.FrameLayout/android.view.ViewGroup/android.widget.FrameLayout[2]/android.widget.LinearLayout/android.widget.ScrollView/android.widget.LinearLayout/android.widget.Button[1]')
        btn.click()

        sentry_sdk.add_breadcrumb(
            category='btn.click',
            message='clicked button via xpath',
            level='info',
        )
        
        android_emu_driver.launch_app()

        sentry_sdk.capture_message("launched app")
    
    except Exception as err:
        sentry_sdk.capture_message("exception handling")
        if err:
            sentry_sdk.capture_exception(err)
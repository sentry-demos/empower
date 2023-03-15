import sentry_sdk
from appium.webdriver.common.appiumby import AppiumBy

# Clicks the Unhandled Error button - NegativeArraySizeException - the button says RTE and Strip PII
def test_unhandlederror2_android(android_emu_driver):

    try:
        # navigate to list app
        android_emu_driver.find_element(AppiumBy.ACCESSIBILITY_ID, 'More').click()
        android_emu_driver.find_element(AppiumBy.ID, 'com.example.vu.android:id/content').click()

        sentry_sdk.add_breadcrumb(
            category='btn.click',
            message='navigated to list app via accessibility_id and xpath elements',
            level='info',
        )

        # trigger error
        android_emu_driver.find_element(AppiumBy.ID, 'com.example.vu.android:id/negative_index').click()

        sentry_sdk.add_breadcrumb(
            category='btn.click',
            message='clicked button via xpath',
            level='info',
        )

        android_emu_driver.launch_app()

    except Exception as err:
        sentry_sdk.capture_exception(err)

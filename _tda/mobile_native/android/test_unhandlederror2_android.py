import time
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

        time.sleep(2)

        android_emu_driver.execute_script('mobile: startActivity', {
            'component': 'com.example.vu.android/.empowerplant.EmpowerPlantActivity',
            'action': 'android.intent.action.MAIN',
            'extras': [['z', 'relaunch_for_send', 'true']]
        })

        # sleep after relaunch to make sure error (+ traces + replays) makes it to the server
        time.sleep(10)

    except Exception as err:
        sentry_sdk.capture_exception(err)

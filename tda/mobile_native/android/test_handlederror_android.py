import sentry_sdk
from appium.webdriver.common.appiumby import AppiumBy

# Clicks the Handled Error button that says ArrayIndexOutOfBoundsException
def test_handlederror_android(android_emu_driver):

    try:
        # navigate to list app
        android_emu_driver.find_element(AppiumBy.ACCESSIBILITY_ID, 'More').click()
        android_emu_driver.find_element(AppiumBy.ID, 'com.example.vu.android:id/content').click()

        # trigger error
        android_emu_driver.find_element(AppiumBy.ID, 'com.example.vu.android:id/handled_exception').click()
        
    except Exception as err:
        sentry_sdk.capture_exception(err)
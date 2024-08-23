import sentry_sdk
from appium.webdriver.common.appiumby import AppiumBy

def test_uncaughtthrownerror_react_native_android(android_react_native_emu_driver):

    try:
        # click into list app screen
        android_react_native_emu_driver.find_element(AppiumBy.XPATH, '//android.widget.FrameLayout[@resource-id="android:id/content"]/android.widget.FrameLayout/android.view.ViewGroup/android.view.ViewGroup/android.view.ViewGroup/android.view.ViewGroup[2]/android.view.View/android.view.View[3]').click()

        # trigger error
        btn = android_react_native_emu_driver.find_element(AppiumBy.XPATH, '//android.widget.TextView[@text="Uncaught Thrown Error"]')
        btn.click()
        # launch app again or the error does not get sent to Sentry
        android_react_native_emu_driver.launch_app()

    except Exception as err:
        sentry_sdk.capture_exception(err)

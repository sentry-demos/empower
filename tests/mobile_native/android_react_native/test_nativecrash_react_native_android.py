import sentry_sdk
from appium.webdriver.common.appiumby import AppiumBy

def test_nativecrash_react_native_android(android_react_native_emu_driver):
    sentry_sdk.set_tag("pytestName", "test_nativecrash_react_native_android")

    try:
        # click into list app screen
        android_react_native_emu_driver.find_element(AppiumBy.XPATH, '/hierarchy/android.widget.FrameLayout/android.widget.LinearLayout/android.widget.FrameLayout/android.widget.LinearLayout/android.widget.FrameLayout/android.widget.FrameLayout/android.view.ViewGroup/android.view.ViewGroup/android.view.ViewGroup/android.view.ViewGroup/android.view.ViewGroup/android.view.ViewGroup/android.view.ViewGroup/android.view.ViewGroup[1]/android.widget.Button[1]/android.widget.TextView').click()
        
        # trigger crash
        btn = android_react_native_emu_driver.find_element(AppiumBy.XPATH, '/hierarchy/android.widget.FrameLayout/android.widget.LinearLayout/android.widget.FrameLayout/android.widget.LinearLayout/android.widget.FrameLayout/android.widget.FrameLayout/android.view.ViewGroup/android.view.ViewGroup/android.view.ViewGroup/android.view.ViewGroup/android.view.ViewGroup/android.view.ViewGroup/android.view.ViewGroup/android.widget.ScrollView/android.view.ViewGroup/android.view.ViewGroup/android.view.ViewGroup[2]/android.view.ViewGroup[11]/android.widget.TextView')
        btn.click()
        # launch app again or the error does not get sent to Sentry
        android_react_native_emu_driver.launch_app()

    except Exception as err:
        sentry_sdk.capture_exception(err)
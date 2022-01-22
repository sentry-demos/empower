import random

# Unhandled Exception - This clicks the 'Uncaught Thrown Error' button in the app
# This error type increments the Crashes count for the release
def test_unhandledpromiserejection_react_native_android(android_react_native_emu_driver):
    btn = android_react_native_emu_driver.find_element_by_xpath('/hierarchy/android.widget.FrameLayout/android.widget.LinearLayout/android.widget.FrameLayout/android.widget.LinearLayout/android.widget.FrameLayout/android.widget.FrameLayout/android.view.ViewGroup/android.view.ViewGroup/android.view.ViewGroup/android.view.ViewGroup/android.view.ViewGroup/android.view.ViewGroup/android.view.ViewGroup/android.widget.ScrollView/android.view.ViewGroup/android.view.ViewGroup/android.view.ViewGroup[2]/android.view.ViewGroup[9]/android.widget.TextView')
    btn.click()

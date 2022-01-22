import random

# Handled Exception
# This error type does not increment the Crash Count for the release, 
# but the UI in Release dashboard separates from Handled vs Handled, so good to capture some of these, for having a more diverse data set.
def test_captureexception_react_native_android(android_react_native_emu_driver):
    btn = android_react_native_emu_driver.find_element_by_xpath('/hierarchy/android.widget.FrameLayout/android.widget.LinearLayout/android.widget.FrameLayout/android.widget.LinearLayout/android.widget.FrameLayout/android.widget.FrameLayout/android.view.ViewGroup/android.view.ViewGroup/android.view.ViewGroup/android.view.ViewGroup/android.view.ViewGroup/android.view.ViewGroup/android.view.ViewGroup/android.widget.ScrollView/android.view.ViewGroup/android.view.ViewGroup/android.view.ViewGroup[2]/android.view.ViewGroup[5]/android.widget.TextView')
    btn.click()

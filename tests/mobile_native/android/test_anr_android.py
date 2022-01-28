import time

# Application Not Responding button
def test_anr_android(android_emu_driver):
    btn = android_emu_driver.find_element_by_xpath('/hierarchy/android.widget.FrameLayout/android.widget.LinearLayout/android.widget.FrameLayout/android.view.ViewGroup/android.widget.FrameLayout[2]/android.widget.LinearLayout/android.widget.ScrollView/android.widget.LinearLayout/android.widget.Button[4]')
    btn.click()

    time.sleep(10)

    android_emu_driver.launch_app()

'''
py.test -s -n 4 mobile_native/android/test_unhandlederror_android.py
py.test -s -n 4 mobile_native/android/test_unhandlederror2_android.py
py.test -s -n 4 mobile_native/android/test_handlederror_android.py
py.test -s -n 4 mobile_native/android/test_anr_android.py
py.test -s -n 4 mobile_native/android/test_nativecrash_android.py
py.test -s -n 4 mobile_native/android/test_nativemessage_android.py
'''
# Clicks the Unhandled Error button that says ArithmeticException
def test_unhandlederror_android(android_emu_driver):
    btn = android_emu_driver.find_element_by_xpath('/hierarchy/android.widget.FrameLayout/android.widget.LinearLayout/android.widget.FrameLayout/android.view.ViewGroup/android.widget.FrameLayout[2]/android.widget.LinearLayout/android.widget.ScrollView/android.widget.LinearLayout/android.widget.Button[1]')
    btn.click()
    
    android_emu_driver.launch_app()
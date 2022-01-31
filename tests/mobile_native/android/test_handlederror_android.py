# Clicks the Handled Error button that says ArrayIndexOutOfBoundsException
def test_handlederror_android(android_emu_driver):
    btn = android_emu_driver.find_element_by_xpath('/hierarchy/android.widget.FrameLayout/android.widget.LinearLayout/android.widget.FrameLayout/android.view.ViewGroup/android.widget.FrameLayout[2]/android.widget.LinearLayout/android.widget.ScrollView/android.widget.LinearLayout/android.widget.Button[3]')
    btn.click()

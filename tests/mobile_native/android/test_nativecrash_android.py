# NDK/C++ Native Crash SIGSEGV button
def test_nativecrash_android(android_emu_driver):
    btn = android_emu_driver.find_element_by_accessibility_id('').click()
    btn.click()
    
    # add_to_cart_btn = android_emu_driver.find_element_by_xpath('/hierarchy/android.widget.FrameLayout/android.widget.LinearLayout/android.widget.FrameLayout/android.view.ViewGroup/android.widget.FrameLayout[2]/android.view.ViewGroup/android.widget.LinearLayout/android.widget.FrameLayout/androidx.recyclerview.widget.RecyclerView/android.widget.LinearLayout[1]/android.widget.LinearLayout/android.widget.LinearLayout/android.widget.Button')
    # add_to_cart_btn.click()

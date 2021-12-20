import time

def test_checkout_android(android_emu_driver):
    android_emu_driver.find_element_by_accessibility_id('shopping cart').click() #toolstore button

    add_to_cart_btn = android_emu_driver.find_element_by_xpath('/hierarchy/android.widget.FrameLayout/android.widget.LinearLayout/android.widget.FrameLayout/android.view.ViewGroup/android.widget.FrameLayout[2]/android.view.ViewGroup/android.widget.LinearLayout/android.widget.FrameLayout/androidx.recyclerview.widget.RecyclerView/android.widget.LinearLayout[1]/android.widget.LinearLayout/android.widget.LinearLayout/android.widget.Button')
    add_to_cart_btn.click()
    add_to_cart_btn.click()
    add_to_cart_btn.click()
    add_to_cart_btn.click()


    android_emu_driver.find_element_by_xpath('/hierarchy/android.widget.FrameLayout/android.widget.LinearLayout/android.widget.FrameLayout/android.view.ViewGroup/android.widget.FrameLayout[1]/android.view.ViewGroup/androidx.appcompat.widget.LinearLayoutCompat/android.widget.FrameLayout/android.widget.ImageView').click()
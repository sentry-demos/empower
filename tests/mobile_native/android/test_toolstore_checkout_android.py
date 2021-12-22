import time

# 'Regular' as in non-react-native
def test_checkout_regular_android(android_emu_driver):
    # Toolstore button
    android_emu_driver.find_element_by_accessibility_id('shopping cart').click()

    # Add items to cart
    add_to_cart_btn = android_emu_driver.find_element_by_xpath('/hierarchy/android.widget.FrameLayout/android.widget.LinearLayout/android.widget.FrameLayout/android.view.ViewGroup/android.widget.FrameLayout[2]/android.view.ViewGroup/android.widget.LinearLayout/android.widget.FrameLayout/androidx.recyclerview.widget.RecyclerView/android.widget.LinearLayout[1]/android.widget.LinearLayout/android.widget.LinearLayout/android.widget.Button')
    add_to_cart_btn.click()
    add_to_cart_btn.click()
    add_to_cart_btn.click()
    add_to_cart_btn.click()

    # Checkout button
    android_emu_driver.find_element_by_xpath('/hierarchy/android.widget.FrameLayout/android.widget.LinearLayout/android.widget.FrameLayout/android.view.ViewGroup/android.widget.FrameLayout[1]/android.view.ViewGroup/androidx.appcompat.widget.LinearLayoutCompat/android.widget.FrameLayout/android.widget.ImageView').click()

    time.sleep(5)

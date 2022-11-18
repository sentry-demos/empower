import sentry_sdk

def test_checkout_react_native_ios(ios_react_native_sim_driver):
    sentry_sdk.set_tag("pytestName", "test_checkout_react_native_ios")

    try:
        cart_btn = ios_react_native_sim_driver.find_element_by_xpath('(//XCUIElementTypeOther[@name="Add to Cart"])[1]')
        cart_btn.click()
        cart_btn.click()
        cart_btn.click()
        cart_btn.click()

        ios_react_native_sim_driver.find_element_by_xpath('//XCUIElementTypeButton[@name="Cart"]').click()
        ios_react_native_sim_driver.find_element_by_xpath('//XCUIElementTypeButton[@name="Checkout"]').click()

        ios_react_native_sim_driver.find_element_by_xpath('(//XCUIElementTypeOther[@name="email"])[3]/XCUIElementTypeTextField').click()
        ios_react_native_sim_driver.find_element_by_xpath('(//XCUIElementTypeOther[@name="Place your order"])[2]').click()

    except Exception as err:
        sentry_sdk.capture_exception(err)

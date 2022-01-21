def test_checkout_ios(ios_react_native_sim_driver):
    ios_react_native_sim_driver.find_element_by_accessibility_id("Empower Plant").click()

    btn = ios_react_native_sim_driver.find_element_by_xpath('(//XCUIElementTypeOther[@name="Add to Cart"])[1]')
    btn.click()
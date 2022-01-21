def test_captureexception_react_native_ios(ios_react_native_sim_driver):
    btn = ios_react_native_sim_driver.find_element_by_accessibility_id("Capture Exception")
    btn.click()

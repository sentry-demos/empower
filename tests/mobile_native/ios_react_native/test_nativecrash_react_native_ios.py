def test_nativecrash_react_native_ios(ios_react_native_sim_driver):
    btn = ios_react_native_sim_driver.find_element_by_accessibility_id("Native Crash")
    btn.click()

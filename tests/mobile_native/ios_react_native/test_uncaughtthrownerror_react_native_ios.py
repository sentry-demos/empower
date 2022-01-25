def test_uncaughtthrownerror_react_native_ios(ios_react_native_sim_driver):
    btn = ios_react_native_sim_driver.find_element_by_accessibility_id("Uncaught Thrown Error")
    btn.click()
    # launch app again or the error does not get sent to Sentry
    ios_react_native_sim_driver.launch_app()

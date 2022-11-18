import sentry_sdk

def test_checkout_ios(ios_sim_driver):
    sentry_sdk.set_tag("pytestName", "test_checkout_ios")

    try:
        first_item = ios_sim_driver.find_element_by_xpath('//XCUIElementTypeApplication[@name="EmpowerPlant"]/XCUIElementTypeWindow/XCUIElementTypeOther/XCUIElementTypeOther/XCUIElementTypeOther/XCUIElementTypeOther/XCUIElementTypeOther/XCUIElementTypeOther/XCUIElementTypeTable[1]/XCUIElementTypeCell[1]/XCUIElementTypeOther[1]/XCUIElementTypeOther')
        first_item.click()
        first_item.click()
        first_item.click()
        first_item.click()

        ios_sim_driver.find_element_by_accessibility_id("Cart").click()
        ios_sim_driver.find_element_by_accessibility_id("Purchase").click()

        # wait for confirmation of purchase? (currently nothing happens)

    except Exception as err:
        sentry_sdk.capture_exception(err)
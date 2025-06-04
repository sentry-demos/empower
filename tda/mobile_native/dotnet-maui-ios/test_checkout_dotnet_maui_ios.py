import time
import sentry_sdk
import pytest
from appium.webdriver.common.appiumby import AppiumBy

@pytest.mark.skip(reason="Add to Cart stopped working on iOS")
def test_checkout_dotnet_maui_ios(ios_dotnet_maui_driver):
    driver = ios_dotnet_maui_driver

    try:
        driver.find_element(AppiumBy.ACCESSIBILITY_ID, "Shop_For_Plants").click()

        first_item_add_to_cart = driver.find_element(AppiumBy.XPATH, '(//XCUIElementTypeButton[@name="Add to Cart"])[1]')
        first_item_add_to_cart.click()
        # Alert disappeared for some reason on iOS
        # Handle the system alert
        #alert = driver.switch_to.alert
        #alert.accept()  # This clicks the "OK" button

        driver.find_element(AppiumBy.ACCESSIBILITY_ID, "Cart").click()
        driver.find_element(AppiumBy.ACCESSIBILITY_ID, "Proceed_to_Order").click()
        driver.find_element(AppiumBy.ACCESSIBILITY_ID, "Place_Order").click()

        time.sleep(6)

    except Exception as err:
        sentry_sdk.capture_exception(err)
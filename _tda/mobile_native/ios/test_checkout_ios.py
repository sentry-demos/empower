import time
import sentry_sdk
from appium.webdriver.common.appiumby import AppiumBy

def test_checkout_ios(ios_sim_driver):

    try:
        first_item = ios_sim_driver.find_element(AppiumBy.ACCESSIBILITY_ID, "AddToCart_Botana Voice")
        first_item.click()
        first_item.click()
        first_item.click()
        first_item.click()

        ios_sim_driver.find_element(AppiumBy.ACCESSIBILITY_ID, "Cart").click()
        ios_sim_driver.find_element(AppiumBy.ACCESSIBILITY_ID, "Purchase").click()

        time.sleep(4)

    except Exception as err:
        sentry_sdk.capture_exception(err)
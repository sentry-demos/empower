import time
import sentry_sdk
from appium.webdriver.common.appiumby import AppiumBy
from selenium.common.exceptions import NoSuchElementException

# Must match driver.implicitly_wait() in conftest.py ios_sim_driver
DEFAULT_IMPLICIT_WAIT = 20


def find_first_present(driver, accessibility_ids, timeout=DEFAULT_IMPLICIT_WAIT):
    driver.implicitly_wait(0)
    try:
        deadline = time.monotonic() + timeout
        while True:
            for accessibility_id in accessibility_ids:
                elements = driver.find_elements(AppiumBy.ACCESSIBILITY_ID, accessibility_id)
                if elements:
                    return accessibility_id, elements[0]
            if time.monotonic() >= deadline:
                raise NoSuchElementException(f"None of {accessibility_ids} found")
            time.sleep(1)
    finally:
        driver.implicitly_wait(DEFAULT_IMPLICIT_WAIT)


def test_checkout_ios(ios_sim_driver):

    try:
        first_item = ios_sim_driver.find_element(AppiumBy.ACCESSIBILITY_ID, "AddToCart_Botana Voice")
        first_item.click()
        first_item.click()
        first_item.click()
        first_item.click()

        ios_sim_driver.find_element(AppiumBy.ACCESSIBILITY_ID, "Cart").click()

        # 0.0.44 and older purchase from the Cart screen, newer builds add a Checkout screen
        button_id, button = find_first_present(ios_sim_driver, ["Purchase", "Checkout"])
        button.click()
        if button_id == "Checkout":
            ios_sim_driver.find_element(AppiumBy.ACCESSIBILITY_ID, "PlaceOrder").click()

        time.sleep(4)

    except Exception as err:
        sentry_sdk.capture_exception(err)
        raise err

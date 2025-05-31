import time
import sentry_sdk
from appium.webdriver.common.appiumby import AppiumBy

def test_checkout_dotnet_maui_android(android_dotnet_maui_driver):
    driver = android_dotnet_maui_driver

    try:
        driver.find_element(AppiumBy.ID, "io.sentry.dotnet.maui.empowerplant:id/Shop_For_Plants").click()

        first_item_add_to_cart = driver.find_element(AppiumBy.ANDROID_UIAUTOMATOR,
                                                     'new UiSelector().text("Add to Cart").instance(0)')
        first_item_add_to_cart.click()

        # Handle the alert (seems non-native)
        ok_button = driver.find_element(AppiumBy.ANDROID_UIAUTOMATOR,
                                        'new UiSelector().resourceId("android:id/button2")')
        ok_button.click()

        driver.find_element(AppiumBy.ACCESSIBILITY_ID, "Cart").click() # unclear why different from the rest
        driver.find_element(AppiumBy.ID, "io.sentry.dotnet.maui.empowerplant:id/Proceed_to_Order").click()
        driver.find_element(AppiumBy.ID, "io.sentry.dotnet.maui.empowerplant:id/Place_Order").click()

        # "Go Spend More" button: new UiSelector().resourceId("android:id/button2")
        time.sleep(4)

    except Exception as err:
        sentry_sdk.capture_exception(err)
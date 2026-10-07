import time
import sentry_sdk
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Clicks the Handled Error button that says ArrayIndexOutOfBoundsException
def test_handlederror_android(android_emu_driver):

    try:
        # navigate to list app
        android_emu_driver.find_element(AppiumBy.ACCESSIBILITY_ID, 'More').click()
        WebDriverWait(android_emu_driver, 10).until(
            EC.element_to_be_clickable((AppiumBy.ID, 'com.example.vu.android:id/content'))
        ).click()

        # trigger error
        android_emu_driver.find_element(AppiumBy.ID, 'com.example.vu.android:id/handled_exception').click()

        time.sleep(4)
    except Exception as err:
        sentry_sdk.capture_exception(err)
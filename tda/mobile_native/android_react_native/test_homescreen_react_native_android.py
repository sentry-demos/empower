import sentry_sdk
from appium.webdriver.common.appiumby import AppiumBy

def test_homescreen_react_native_android(android_react_native_emu_driver, random):

    try:
        # click into list app screen
        android_react_native_emu_driver.find_element(AppiumBy.XPATH, '//android.widget.FrameLayout[@resource-id="android:id/content"]/android.widget.FrameLayout/android.view.ViewGroup/android.view.ViewGroup/android.view.ViewGroup/android.view.ViewGroup[2]/android.view.View/android.view.View[3]').click()

        # Handled Exceptions - This clicks the Handled Exception' button in the app
        # This error type does not increment the Crash Count for the release,
        # but the UI in Release dashboard separates from Handled vs Handled, so good to capture some of these, for having a more diverse data set.
        # 40% of the time this will error.
        if random.randint(1,10) < 3:
            android_react_native_emu_driver.find_element(AppiumBy.XPATH, '//android.widget.TextView[@text="Capture Exception"]').click()

        # Unhandled Exception - This clicks the 'Uncaught Thrown Error' button in the app
        # This error type increments the Crashes count for the release
        # 40% of the time this will error.
        if random.randint(1,10) < 3:
            android_react_native_emu_driver.find_element(AppiumBy.XPATH, '//android.widget.TextView[@text="Uncaught Thrown Error"]').click()


        # TODO - select by something other than a xpath. This may require a <TextView> in react-native instead of a <Text>
        # android_react_native_emu_driver.find_element(AppiumBy.XPATH, '//*[@text="Unhandled Promise Rejection"]').click()

        # TODO - add more types of unhandled errors. This button not work, because the xpath could not be found, despite double checking in Appium Inpsector that it was the right one.
        # Unhandled Promise Rejection - increments the Crashes count
        # android_react_native_emu_driver.find_element(AppiumBy.XPATH, '/hierarchy/android.widget.FrameLayout/android.widget.LinearLayout/android.widget.FrameLayout/android.widget.LinearLayout/android.widget.FrameLayout/android.widget.FrameLayout/android.view.ViewGroup/android.view.ViewGroup/android.view.ViewGroup/android.view.ViewGroup/android.view.ViewGroup/android.view.ViewGroup/android.view.ViewGroup/android.widget.ScrollView/android.view.ViewGroup/android.view.ViewGroup/android.view.ViewGroup[2]/android.view.ViewGroup[9]/android.widget.TextView').click()

    except Exception as err:
        sentry_sdk.capture_exception(err)




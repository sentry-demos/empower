import time

import sentry_sdk
from appium.webdriver.common.appiumby import AppiumBy

# Total number of taps used to trigger the ANR dialog.
# The first tap is a normal Appium click; the remainder are sent via ADB
# while the main thread is frozen.
_ANR_TAP_COUNT = 10

# Seconds to wait for the system to recover after dismissing the ANR dialog.
_ANR_RECOVERY_WAIT_SECONDS = 3


def test_anr_flutter_android(android_flutter_driver):
    try:
        # Open the drawer and click ANR — the app closes the drawer then
        # busy-loops the main thread for ~10 s.
        android_flutter_driver.find_element(
            AppiumBy.ACCESSIBILITY_ID, "Open navigation menu"
        ).click()
        android_flutter_driver.find_element(
            AppiumBy.ACCESSIBILITY_ID, "ANR (Android)"
        ).click()

        # Main thread is now blocked. Send the remaining taps via ADB so they
        # accumulate as pending input events. Android raises the ANR dialog
        # once ~5 s of unresponsiveness is detected (configured in
        # AndroidManifest.xml). Each call is expected to time out.
        for _ in range(_ANR_TAP_COUNT - 1):
            try:
                android_flutter_driver.execute_script("mobile: shell", {
                    "command": "input",
                    "args": ["tap", "200", "200"],
                    "timeout": 5000,
                })
            except Exception:
                pass  # Expected to fail while the main thread is frozen

        # Dismiss the ANR dialog by selecting 'Close App'.
        android_flutter_driver.find_element(
            AppiumBy.ID, "android:id/aerr_close"
        ).click()

        # Allow time for the ANR event to be sent to Sentry
        time.sleep(_ANR_RECOVERY_WAIT_SECONDS)

    except Exception as err:
        sentry_sdk.capture_exception(err)

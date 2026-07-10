import time

import sentry_sdk
from appium.webdriver.common.appiumby import AppiumBy

# Seconds to let the in-app WebView load the page and for the Flutter-side
# WebView transaction + propagated trace headers to reach Sentry.
_WEBVIEW_LOAD_WAIT_SECONDS = 8


def test_webview_flutter_android(android_flutter_driver):
    """Web View journey: opens empower-plant.com inside the app's in-app WebView.

    This starts a dedicated transaction on a fresh trace and attaches the
    sentry-trace/baggage so the loaded web page can continue the trace
    (Flutter -> WebView distributed tracing).
    """
    try:
        # ------------------------------------------------------------------
        # Open the drawer and launch the Web View
        # ------------------------------------------------------------------
        android_flutter_driver.find_element(
            AppiumBy.ACCESSIBILITY_ID, "Open navigation menu"
        ).click()
        android_flutter_driver.find_element(
            AppiumBy.ACCESSIBILITY_ID, "Web View"
        ).click()

        # Confirm the Web View screen opened (its app bar title).
        android_flutter_driver.find_element(
            AppiumBy.ACCESSIBILITY_ID, "Empower Plant (Web)"
        )

        # Allow the page to load and the WebView transaction/trace to be sent.
        time.sleep(_WEBVIEW_LOAD_WAIT_SECONDS)

    except Exception as err:
        sentry_sdk.capture_exception(err)

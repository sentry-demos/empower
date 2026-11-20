import sentry_sdk
from conftest import ios_tap


def test_checkout_ios(ios_sim_driver):

    try:
        # Checkout only sends quantities for 4 fixed plants; 4x Botana Voice makes /checkout return 500
        for _ in range(4):
            ios_tap(ios_sim_driver, "AddToCart_Botana Voice")
        ios_tap(ios_sim_driver, "Cart")
        ios_tap(ios_sim_driver, "Checkout")
        ios_tap(ios_sim_driver, "ApplyPromo", wait=2)
        ios_tap(ios_sim_driver, "PlaceOrder")
        # Shown only after the 500 is captured as a PurchaseError; the form message is prefilled after it opens
        ios_tap(ios_sim_driver, "CheckoutFeedback", wait=2)
        # Let events, logs and replay upload before the session kills the app
        ios_tap(ios_sim_driver, "io.sentry.feedback.form.submit", wait=10)

    except Exception as err:
        sentry_sdk.capture_exception(err)
        raise err

import time
import sentry_sdk
from urllib.parse import urlencode

def test_add_to_cart_join(desktop_web_driver, endpoints, random, batch_size, backend, sleep_length):
    sentry_sdk.set_tag("pytestName", "test_add_to_cart_join")

    for endpoint in endpoints['react_endpoints']:
        endpoint_products_join = endpoint + "/products-join"
        sentry_sdk.set_tag("endpoint", endpoint_products_join)

        for i in range(batch_size):
            # Ensures a different backend endpoint gets picked each time
            url = ""
            # TODO make a query_string builder function for sharing this across tests
            query_string = { 
                # 'ruby' /products /checkout endpoints not available yet
                'backend': backend(exclude=['ruby', 'laravel'])
            }
            url = endpoint_products_join + '?' + urlencode(query_string)

            desktop_web_driver.get(url)
            time.sleep(sleep_length() + sleep_length() + 1)
        
        # Checkout button not clicked yet in /products-join

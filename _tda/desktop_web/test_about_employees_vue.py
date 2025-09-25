import time
import sentry_sdk

def test_about_employees_vue(desktop_web_driver, endpoints, random, batch_size, sleep_length):

    for endpoint in [endpoints.vue_endpoint]:

        endpoint = endpoint + "/about"

        sentry_sdk.set_tag("endpoint", endpoint)

        for i in range(batch_size):
            # TODO in application-monitoring/vue repo
            # should be able to click each employee and it navigates to an /:employee page
            # this demonstrates parameterized transactions in Vue

            try:
                desktop_web_driver.get(endpoint)

            except Exception as err:
                if err:
                    sentry_sdk.capture_exception(err)

            time.sleep(sleep_length())

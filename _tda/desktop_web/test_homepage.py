import time
import sentry_sdk
from urllib.parse import urlencode
from datetime import datetime


# This test is for the homepage '/' transaction
def test_homepage(desktop_web_driver, endpoints, random, batch_size, backend, sleep_length):

    # n - float in [0,1]
    def probability(p):
        return random.random() <= p

    # Find what week it is, as this is used as the patch version in YY.MM.W like 22.6.2
    d=datetime.today()
    week=str((d.day-1)//7+1)
    week=int(week)

    # For setting a different Crash Free Rate each week
    upper_bound = 0

    if week % 2 == 0:
        # even patch version, e.g. 22.6.2
        upper_bound = .2
    else:
        # odd patch version, e.g. 22.6.3
        upper_bound = .4


    for endpoint in [endpoints.react_endpoint]:
        sentry_sdk.set_tag("endpoint", endpoint)

        for i in range(batch_size):
            # Randomize the Failure Rate between 1% and 20% or 40%, depending what week it is. Returns values like 0.02, 0.14, 0.37
            n = random.uniform(0.01, upper_bound)

            crash = probability(n) and 1.0 or 0.0
            errnum = random.randint(0, 999) # decides which error type is thrown

            if crash == 1.0: # only run test if crash is certainrun test to cause homepage to force crash,
                             # otherwise don't run test (as test_checkout.py starts at /)
                # This query string is parsed by utils/errors.js wherever the 'crasher' function is used
                # and causes the page to periodically crash, for Release Health
                # TODO make a query_string builder function for sharing this across tests
                query_string = {
                    'backend': backend(),
                    'crash': "%s" % (crash),
                    'errnum': "%d" % (errnum),
                    'crash_authorized': 'true'
                }
                url = endpoint + '?' + urlencode(query_string)

                desktop_web_driver.get(url)
                time.sleep(sleep_length() + sleep_length() + 1)

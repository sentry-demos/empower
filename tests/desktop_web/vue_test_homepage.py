import time
import yaml
import random
import sentry_sdk
from urllib.parse import urlencode
from collections import OrderedDict

# This test is for the homepage '/' transaction
@pytest.mark.skip(reason="testing vue only right now...")
def test_homepage(desktop_web_driver):
    sentry_sdk.set_tag("pytestName", "test_homepage")

    endpoint = "https://application-monitoring-vue-dot-sales-engineering-sf.appspot.com/"

    sentry_sdk.set_tag("endpoint", endpoint)

    for i in range(random.randrange(20)):
        # TODO 
        # querystring support for 'se' and 'backend' tags
        
        # TODO
        # No randomization of failures, because Vue app is not setup to do this right now.

        # TODO
        # "/products" not needed right now, because Home page in Vue app loads the products

        desktop_web_driver.get(endpoint)
        time.sleep(random.randrange(3) + 3)

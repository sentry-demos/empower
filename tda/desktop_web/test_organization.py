# ### COMMENTING OUT since we know have /products-fes (which generates uncompressed asset perf-issue) ###


# import time
# import pytest
# import sentry_sdk
# from urllib.parse import urlencode

# def test_organization(desktop_web_driver, endpoints, random, batch_size, backend, sleep_length):
#     sentry_sdk.set_tag("pytestName", "test_organization")

#     for endpoint in endpoints.react_endpoints:
#         endpoint_organization = endpoint + "/organization"
#         sentry_sdk.set_tag("endpoint", endpoint_organization)

#         query_string = {
#             # only run against 'flask'
#             'backend': backend(include=['flask'])
#         }
#         url = endpoint_organization + '?' + urlencode(query_string)

#         for i in range(batch_size):

#             desktop_web_driver.get(url)

#             # images are being loaded in /about from Cloud Storage
#             time.sleep(sleep_length())

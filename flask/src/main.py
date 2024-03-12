import datetime
import operator
import os
import random
import requests
import time
from flask import Flask, json, request, make_response, send_from_directory
from flask_cors import CORS
import dotenv
from .db import get_products, get_products_join, get_inventory
from .utils import parseHeaders, get_iterator
import sentry_sdk
from sentry_sdk import metrics
from sentry_sdk.integrations.flask import FlaskIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration

RUBY_CUSTOM_HEADERS = ['se', 'customerType', 'email']
pests = ["aphids", "thrips", "spider mites", "lead miners", "scale", "whiteflies", "earwigs", "cutworms", "mealybugs",
         "fungus gnats"]

RELEASE = None
DSN = None
ENVIRONMENT = None
RUBY_BACKEND = None
RUN_SLOW_PROFILE = None


def before_send(event, hint):
    # 'se' tag may have been set in app.before_request
    se = None
    if 'tags' in event.keys() and 'se' in event['tags']:
        se = event['tags']['se']

    if se not in [None, "undefined"]:
        if se.startswith('prod-tda-'):
            event['fingerprint'] = ['{{ default }}', se, RELEASE]
        else:
            event['fingerprint'] = ['{{ default }}', se]

    return event


def traces_sampler(sampling_context):
    sentry_sdk.set_context("sampling_context", sampling_context)
    REQUEST_METHOD = sampling_context['wsgi_environ']['REQUEST_METHOD']
    if REQUEST_METHOD == 'OPTIONS':
        return 0.0
    else:
        return 1.0


class MyFlask(Flask):
    def __init__(self, import_name, *args, **kwargs):
        global RELEASE, DSN, ENVIRONMENT, RUBY_BACKEND, RUN_SLOW_PROFILE;
        dotenv.load_dotenv()

        RELEASE = os.environ["RELEASE"]
        DSN = os.environ["FLASK_APP_DSN"]
        ENVIRONMENT = os.environ["FLASK_ENV"]
        RUBY_BACKEND = os.environ["RUBY_BACKEND"]

        RUN_SLOW_PROFILE = True
        if "RUN_SLOW_PROFILE" in os.environ:
            RUN_SLOW_PROFILE = os.environ["RUN_SLOW_PROFILE"].lower() == "true"

        print("> DSN", DSN)
        print("> RELEASE", RELEASE)
        print("> ENVIRONMENT", ENVIRONMENT)

        sentry_sdk.init(
            dsn=DSN,
            release=RELEASE,
            environment=ENVIRONMENT,
            integrations=[FlaskIntegration(), SqlalchemyIntegration()],
            traces_sample_rate=1.0,
            before_send=before_send,
            traces_sampler=traces_sampler,
            _experiments={
                "enable_metrics": True,
                "profiles_sample_rate": 1.0
            }
        )

        super(MyFlask, self).__init__(import_name, *args, **kwargs)


app = MyFlask(__name__)
CORS(app)


@app.route('/checkout', methods=['POST'])
def checkout():
    sentry_sdk.metrics.incr(
        key="endpoint_call",
        value=1,
        tags={"endpoint": "/checkout", "method": "POST"},
    )

    order = json.loads(request.data)
    cart = order["cart"]
    form = order["form"]

inventory = []
try:
    with sentry_sdk.start_span(op="/checkout.get_inventory", description="function"):
        with sentry_sdk.metrics.timing(key="checkout.get_inventory.execution_time"):
            inventory = get_inventory(cart)
except Exception as err:
    raise (err)

print("> /checkout inventory", inventory)

with sentry_sdk.start_span(op="process_order", description="function"):
    quantities = cart['quantities']
    for cartItem in quantities:
        for inventoryItem in inventory:
            print("> inventoryItem.count", inventoryItem['count'])
            if (inventoryItem['count'] < quantities[cartItem]):
                sentry_sdk.metrics.incr(key="checkout.failed")
                raise Exception("Not enough inventory for product")
    if len(inventory) == 0 or len(quantities) == 0:
        raise Exception("Not enough inventory for product")

response = make_response("success")
return response


@app.route('/success', methods=['GET'])
def success():
    sentry_sdk.metrics.incr(
        key="endpoint_call",
        value=1,
        tags={"endpoint": "/success", "method": "GET"},
    )

    return "success from flask"


@app.route('/products', methods=['GET'])
def products():
    sentry_sdk.metrics.incr(
        key="endpoint_call",
        value=1,
        tags={"endpoint": "/products", "method": "GET"},
    )

    try:
        with sentry_sdk.start_span(op="/products.get_products", description="function"):
            with sentry_sdk.metrics.timing(key="products.get_products.execution_time"):
                rows = get_products()

            if RUN_SLOW_PROFILE:
                start_time = time.time()
                productsJSON = json.loads(rows)
                descriptions = [product["description"] for product in productsJSON]
                with sentry_sdk.start_span(op="/get_iterator", description="function"):
                    with sentry_sdk.metrics.timing(key="products.get_iterator.execution_time"):
                        loop = get_iterator(len(descriptions) * 6 - 1)

                    for i in range(loop):
                        time_delta = time.time() - start_time
                        if time_delta > 2:
                            break

                        for i, description in enumerate(descriptions):
                            for pest in pests:
                                if pest in description:
                                    try:
                                        del productsJSON[i:i + 1]
                                    except:
                                        productsJSON = json.loads(rows)
    except Exception as err:
        sentry_sdk.capture_exception(err)
        raise (err)

    try:
        with sentry_sdk.start_span(op="/api_request", description="function"):
            headers = parseHeaders(RUBY_CUSTOM_HEADERS, request.headers)
            r = requests.get(RUBY_BACKEND + "/api", headers=headers)
            r.raise_for_status()  # returns an HTTPError object if an error has occurred during the process
    except Exception as err:
        sentry_sdk.capture_exception(err)

    return rows


@app.route('/products-join', methods=['GET'])
def products_join():
    try:
        with sentry_sdk.start_span(op="/products-join.get_products_join", description="function"):
            rows = get_products_join()
    except Exception as err:
        sentry_sdk.capture_exception(err)
        raise (err)

    try:
        headers = parseHeaders(RUBY_CUSTOM_HEADERS, request.headers)
        r = requests.get(RUBY_BACKEND + "/api", headers=headers)
        r.raise_for_status()  # returns an HTTPError object if an error has occurred during the process
    except Exception as err:
        sentry_sdk.capture_exception(err)

    return rows


@app.route('/handled', methods=['GET'])
def handled_exception():
    try:
        '2' + 2
    except Exception as err:
        sentry_sdk.capture_exception(err)
    return 'failed'


@app.route('/unhandled', methods=['GET'])
def unhandled_exception():
    obj = {}
    obj['keyDoesnt  Exist']


@app.route('/api', methods=['GET'])
def api():
    return "flask /api"


@app.route('/organization', methods=['GET'])
def organization():
    # perform get_products db query 1% of time in order
    #   to populate "Found In" endpoints in Queries
    if random.random() < 0.01:
        rows = get_products()
    return "flask /organization"


@app.route('/connect', methods=['GET'])
def connect():
    return "flask /connect"


@app.route('/product/0/info', methods=['GET'])
def product_info():
    time.sleep(.55)
    return "flask /product/0/info"


# uncompressed assets
@app.route('/uncompressed_assets/<path:path>')
def send_report(path):
    time.sleep(.55)
    response = send_from_directory('../uncompressed_assets', path)
    # `Timing-Allow-Origin: *` allows timing/sizes to visbile in span
    response.headers['Timing-Allow-Origin'] = '*'
    # Overwriting `Content-Type` header to disable compression
    response.headers['Content-Type'] = 'application/octet-stream'
    return response


# compressed assets
@app.route('/compressed_assets/<path:path>')
def send_report_configured_properly(path):
    response = send_from_directory('../compressed_assets', path)
    # `Timing-Allow-Origin: *` allows timing/sizes to visbile in span
    response.headers['Timing-Allow-Origin'] = '*'
    return response


@app.before_request
def sentry_event_context():
    se = request.headers.get('se')
    if se not in [None, "undefined"]:
        sentry_sdk.set_tag("se", se)
    else:
        # sometimes this is the only way to propagate, e.g. when requested through a dynamically
        # inserted HTML tag as in case with (un)compressed_assets
        se = request.args.get('se')
        if se not in [None, "undefined"]:
            sentry_sdk.set_tag("se", se)

    customerType = request.headers.get('customerType')
    if customerType not in [None, "undefined"]:
        sentry_sdk.set_tag("customerType", customerType)

    email = request.headers.get('email')
    if email not in [None, "undefined"]:
        sentry_sdk.set_user({"email": email})

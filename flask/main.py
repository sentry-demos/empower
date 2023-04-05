import datetime
import operator
import os
import requests
import sys
import time
from flask import Flask, json, request, make_response, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv
from db import get_products, get_products_join, get_inventory
from utils import parseHeaders, get_iterator
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
load_dotenv()

PORT = os.environ["PORT"]
RELEASE = os.environ["RELEASE"]
DSN = os.environ["FLASK_APP_DSN"]
ENVIRONMENT = os.environ["FLASK_ENV"]
RUBY_BACKEND = os.environ["RUBY_BACKEND"]
RUBY_CUSTOM_HEADERS = ['se', 'customerType', 'email']

pests = ["aphids", "thrips", "spider mites", "lead miners", "scale", "whiteflies", "earwigs", "cutworms", "mealybugs", "fungus gnats"]
RUN_SLOW_PROFILE = True
if "RUN_SLOW_PROFILE" in os.environ:
    RUN_SLOW_PROFILE = os.environ["RUN_SLOW_PROFILE"].lower() == "true"

print("> DSN", DSN)
print("> RELEASE", RELEASE)
print("> ENVIRONMENT", ENVIRONMENT)

def before_send(event, hint):
    # 'se' tag may have been set in app.before_request
    se = None
    with sentry_sdk.configure_scope() as scope:
        if 'se' in scope._tags:
            se = scope._tags['se']

    if se == "tda":
        event['fingerprint'] = [ '{{ default }}', se, RELEASE ]
    elif se not in [None, "undefined"]:
        event['fingerprint'] = [ '{{ default }}', se]

    return event

def traces_sampler(sampling_context):
    sentry_sdk.set_context("sampling_context", sampling_context)
    REQUEST_METHOD=sampling_context['wsgi_environ']['REQUEST_METHOD']
    if REQUEST_METHOD == 'OPTIONS':
        return 0.0
    else:
        return 1.0

sentry_sdk.init(
    dsn=DSN,
    release=RELEASE,
    environment=ENVIRONMENT,
    integrations=[FlaskIntegration(), SqlalchemyIntegration()],
    traces_sample_rate=1.0,
    before_send=before_send,
    traces_sampler=traces_sampler,
    _experiments={
        "profiles_sample_rate": 1.0
    }
)

app = Flask(__name__)
CORS(app)

@app.route('/checkout', methods=['POST'])
def checkout():
    order = json.loads(request.data)
    cart = order["cart"]
    form = order["form"]

    inventory = []
    try:
        with sentry_sdk.start_span(op="/checkout.get_inventory", description="function"):
            inventory = get_inventory(cart)
    except Exception as err:
        raise(err)

    print("> /checkout inventory", inventory)

    with sentry_sdk.start_span(op="process_order", description="function"):
        quantities = cart['quantities']
        for cartItem in quantities:
            for inventoryItem in inventory:
                print("> inventoryItem.count", inventoryItem['count'])
                if (inventoryItem.count < quantities[cartItem]):
                    raise Exception("Not enough inventory for " + "product")

    response = make_response("success")
    return response

@app.route('/success', methods=['GET'])
def success():
    return "success from flask"

@app.route('/products', methods=['GET'])
def products():
    try:
        with sentry_sdk.start_span(op="/products.get_products", description="function"):
            rows = get_products()
            
            if RUN_SLOW_PROFILE:
                start_time = time.time()
                productsJSON = json.loads(rows)
                descriptions = [product["description"] for product in productsJSON]
                with sentry_sdk.start_span(op="/get_iterator", description="function"):
                    loop = get_iterator(len(descriptions) * 6)
                    for i in range(loop):
                        time_delta = time.time() - start_time
                        if time_delta > 4:
                            break

                        for i, description in enumerate(descriptions):
                            for pest in pests:
                                if pest in description:
                                    try:
                                        del productsJSON[i:i+1]
                                    except:
                                        productsJSON = json.loads(rows)
    except Exception as err:
        sentry_sdk.capture_exception(err)
        raise(err)

    try:
        with sentry_sdk.start_span(op="/api_request", description="function"):
            headers = parseHeaders(RUBY_CUSTOM_HEADERS, request.headers)
            r = requests.get(RUBY_BACKEND + "/api", headers=headers)
            r.raise_for_status() # returns an HTTPError object if an error has occurred during the process
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
        raise(err)

    try:
        headers = parseHeaders(RUBY_CUSTOM_HEADERS, request.headers)
        r = requests.get(RUBY_BACKEND + "/api", headers=headers)
        r.raise_for_status() # returns an HTTPError object if an error has occurred during the process
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
    return "flask /organization"

@app.route('/connect', methods=['GET'])
def connect():
    return "flask /connect"

@app.route('/product/0/info', methods=['GET'])
def product_info():
    time.sleep(.55)
    return "flask /product/0/info"

# uncompressed assets
@app.route('/uc_assets/<path:path>')
def send_report(path):
    time.sleep(.55)
    response = send_from_directory('uc_assets', path)
    # `Timing-Allow-Origin: *` allows timing/sizes to visbile in span
    response.headers['Timing-Allow-Origin'] = '*'
    # Overwriting `Content-Type` header to disable compression
    response.headers['Content-Type'] = 'application/octet-stream'
    return response

# compressed assets
@app.route('/c_assets/<path:path>')
def send_report_configured_properly(path):
    response = send_from_directory('c_assets', path)
    # `Timing-Allow-Origin: *` allows timing/sizes to visbile in span
    response.headers['Timing-Allow-Origin'] = '*'
    return response

@app.before_request
def sentry_event_context():
    se = request.headers.get('se')
    if se not in [None, "undefined"]:
        sentry_sdk.set_tag("se", se)

    customerType = request.headers.get('customerType')
    if customerType not in [None, "undefined"]:
        sentry_sdk.set_tag("customerType", customerType)

    email = request.headers.get('email')
    if email not in [None, "undefined"]:
        sentry_sdk.set_user({ "email" : email })

if __name__ == '__main__':
    i = sys.version_info
    if sys.version_info[0] < 3:
        raise SystemExit("Failed to start: need python3")
    # This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app.
    app.run(host='127.0.0.1', port=PORT, debug=False)

import datetime
import os
import sys
from flask import Flask, json, request, make_response
from flask_cors import CORS
from dotenv import load_dotenv
from db import get_products, get_products_join, get_inventory
from utils import release
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
load_dotenv()

RELEASE = os.environ.get("RELEASE") or release()
DSN = os.getenv("FLASK_APP_DSN")
ENVIRONMENT = os.environ.get("FLASK_ENV") or "production"

print("> DSN", DSN)
print("> RELEASE", RELEASE)
print("> ENVIRONMENT", ENVIRONMENT)

def before_send(event, hint):
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
    traces_sampler=traces_sampler
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
        inventory = get_inventory(cart)
    except Exception as err:
        print(err)
        sentry_sdk.capture_exception(err)
    print("> /checkout inventory", inventory)

    quantities = cart['quantities']
    for cartItem in quantities:
        for inventoryItem in inventory:
            print("> inventoryItem.count", inventoryItem['count'])
            if (inventoryItem.count < quantities[cartItem]):
                raise Exception("Not enough inventory for " + "product")
        
    response = make_response("response from backend")
    return response
 
@app.route('/success', methods=['GET'])
def success():    
    return "successs"

@app.route('/products', methods=['GET'])
def products():    
    print('/products')
    try:
        rows = get_products()
    except Exception as err:
        sentry_sdk.capture_exception(err)
        raise(err)
    return rows

@app.route('/products-join', methods=['GET'])
def products_join():    
    print('/products-join')
    try:
        rows = get_products_join()
    except Exception as err:
        sentry_sdk.capture_exception(err)
        raise(err)
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
    obj['keyDoesntExist']

@app.before_request
def sentry_event_context():
    se = request.headers.get('se')
    print('\n> se', se)
    sentry_sdk.set_tag("se", se)

if __name__ == '__main__':
    i = sys.version_info
    if sys.version_info[0] < 3:
        raise SystemExit("Failed to start: need python3")
    # This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app.
    app.run(host='127.0.0.1', port=8080, debug=False)
import datetime
import os
import sys
# from flask import abort, make_response, jsonify
from flask import Flask, json, request
from flask_cors import CORS
from dotenv import load_dotenv
from db import get_products, get_products_join
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
    # TODO need this still?
    if event['request']['method'] == 'OPTIONS':
        return null
    print("> event", event)
    return event

sentry_sdk.init(
    dsn=DSN,
    release=RELEASE,
    environment=ENVIRONMENT,
    integrations=[FlaskIntegration(), SqlalchemyIntegration()],
    traces_sample_rate=1.0,
    before_send=before_send
)

app = Flask(__name__)
CORS(app)

@app.route('/checkout', methods=['POST'])
def checkout():
    # payload = json.loads(request.data)
    print("1111111")
    print(json.loads(request.data))
    print("2222222")
    # order = json.loads(request.data)
    # print("Processing order for: " + request.headers.get('email'))
    # cart = order["cart"]

    # try:
    #     rows = get_inventory()
    # except Exception as err:
    #     sentry_sdk.capture_exception(err)
    #     raise(err)

    # process_order(cart)

    # try:
    #     rows = update_inventory()
    # except Exception as err:
    #     raise(err)

    return 'Success Checkout'
 
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

if __name__ == '__main__':
    i = sys.version_info
    if sys.version_info[0] < 3:
        raise SystemExit("Failed to start: need python3")
    # This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app.
    app.run(host='127.0.0.1', port=8080, debug=True)
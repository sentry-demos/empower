import os
import random
import requests
import time
import redis
import logging
from datetime import datetime
from flask import Flask, json, jsonify, request, make_response, send_from_directory
from openai import OpenAI
from flask_caching import Cache
from statsig.statsig_user import StatsigUser
from statsig import statsig, StatsigOptions, StatsigEnvironmentTier
import dotenv
from .db import decrement_inventory, get_products, get_products_join, get_inventory, get_promo_code, db
from .utils import parseHeaders, get_iterator, evaluate_statsig_flags
from celery import Celery, states
from celery.exceptions import Ignore
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.resources import Resource
from opentelemetry.semconv.resource import ResourceAttributes
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.redis import RedisInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace.export import BatchSpanProcessor

RUBY_CUSTOM_HEADERS = ['se', 'customerType', 'email']
pests = ["aphids", "thrips", "spider mites", "lead miners", "scale", "whiteflies", "earwigs", "cutworms", "mealybugs",
         "fungus gnats"]

BACKEND_URL_RUBYONRAILS = None
RUN_SLOW_PROFILE = None
tracer = None  # Global OpenTelemetry tracer

NORMAL_SLOW_PROFILE = 2 # seconds
EXTREMELY_SLOW_PROFILE = 24


def redis_request_hook(span, instance, args, kwargs):
    """Custom request hook to capture Redis keys in spans"""
    if span and span.is_recording() and args:
        # args is a tuple like ('GET', 'mykey') or ('SET', 'mykey', 'value', 'EX', 5)
        if len(args) >= 2:
            command = args[0] if isinstance(args[0], str) else str(args[0])
            key = args[1] if isinstance(args[1], str) else str(args[1])
            
            # Set the key as an attribute
            span.set_attribute("db.redis.key", key)
            span.set_attribute("db.statement", f"{command} '{key}'")


class MyFlask(Flask):
    def __init__(self, import_name, *args, **kwargs):
        global BACKEND_URL_RUBYONRAILS, RUN_SLOW_PROFILE, redis_client, cache, tracer;
        dotenv.load_dotenv()

        BACKEND_URL_RUBYONRAILS = os.environ["BACKEND_URL_RUBYONRAILS"]

        RUN_SLOW_PROFILE = True
        if "RUN_SLOW_PROFILE" in os.environ:
            RUN_SLOW_PROFILE = os.environ["RUN_SLOW_PROFILE"].lower() == "true"


        resource = Resource(attributes={
            ResourceAttributes.SERVICE_NAME: "flask-otlp",
        })
        tracer_provider = TracerProvider(resource=resource)
        otlp_endpoint = os.environ.get("OTEL_EXPORTER_OTLP_ENDPOINT")
        if otlp_endpoint:
            headers = {}
            dsn = os.environ.get("FLASKOTLP_DSN")
            if dsn:
                from urllib.parse import urlparse
                public_key = urlparse(dsn).username
                headers["x-sentry-auth"] = f"Sentry sentry_key={public_key}, sentry_version=7"
            exporter = OTLPSpanExporter(endpoint=otlp_endpoint, headers=headers)
            tracer_provider.add_span_processor(BatchSpanProcessor(exporter))
        trace.set_tracer_provider(tracer_provider)
        global tracer
        tracer = trace.get_tracer(__name__)

        statsig.initialize(os.environ["STATSIG_SERVER_KEY"])

        # Instrument with OpenTelemetry BEFORE creating clients
        # This ensures all connections are properly traced
        RequestsInstrumentor().instrument()
        RedisInstrumentor().instrument(request_hook=redis_request_hook)
        
        # Instrument the existing database engine (created at import time in db.py)
        SQLAlchemyInstrumentor().instrument(engine=db)
        
        super(MyFlask, self).__init__(import_name, *args, **kwargs)

        redis_host = os.environ["FLASKOTLP_REDISHOST"]
        redis_port = int(os.environ["FLASKOTLP_REDISPORT"])

        cache_config = {
            "DEBUG": True,
            "CACHE_TYPE": "RedisCache",
            "CACHE_DEFAULT_TIMEOUT": 300,
            "CACHE_REDIS_HOST": redis_host,
            "CACHE_REDIS_PORT": redis_port,
            "CACHE_KEY_PREFIX": None
        }

        self.config.from_mapping(cache_config)
        cache = Cache(self)

        redis_client = redis.Redis(host=redis_host, port=redis_port, decode_responses=True)
        
        # Instrument Flask app after it's fully initialized
        FlaskInstrumentor().instrument_app(self)


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.info("Flask application initialized")

# This ensures CORS headers are applied to ALL responses, including 500 errors
# upgrading flask-cors from 3.0.10 to 6.0.1 and flask from 3.0.0 to 3.1.1 alone did not fix the issue
# doesn't seem to be related to https://github.com/corydolphin/flask-cors/issues/210 as we don't set
# debug=True anywhere. However suspiciously it didn't show up in production/TDA only when testing
# locally against staging.
class CORSWSGIWrapper:
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        def custom_start_response(status, headers, exc_info=None):
            headers.append(('Access-Control-Allow-Origin', '*'))
            headers.append(('Access-Control-Allow-Headers', '*')) # needed for 'customertype' and other "tag headers"
            return start_response(status, headers, exc_info)

        try:
            return self.app(environ, custom_start_response)
        except Exception as e:
            pass
            # If an exception occurs, create a response with CORS headers
            status = '500 Internal Server Error'
            headers = [
                ('Content-Type', 'application/json'),
                ('Access-Control-Allow-Origin', '*'),
                ('Access-Control-Allow-Headers', '*'),
            ]
            response_body = json.dumps({"error": "Internal Server Error"}).encode('utf-8')

            def error_start_response(status, headers, exc_info=None):
                return start_response(status, headers, exc_info)

            error_start_response(status, headers)
            return [response_body]

    def __getattr__(self, name):
        # Delegate attribute access to the underlying Flask app e.g. app.config
        return getattr(self.app, name)


app = MyFlask(__name__)
app = CORSWSGIWrapper(app)


@app.route('/checkout', methods=['POST'])
def checkout():
    logger.info('Received /checkout endpoint request')

    try:
        evaluate_statsig_flags()
    except Exception as e:
        logger.error('Error evaluating Statsig flags')

    order = json.loads(request.data)
    cart = order["cart"]
    form = order["form"]
    validate_inventory = True if "validate_inventory" not in order else order["validate_inventory"] == "true"

    logger.info('Processing /checkout - validating order details')

    inventory = []
    try:
        inventory = get_inventory(cart)
    except Exception as err:
        logger.warn('Failed to get inventory')
        raise (err)

    fulfilled_count = 0
    out_of_stock = [] # list of items that are out of stock
    try:
        if validate_inventory:
            with tracer.start_as_current_span(
                "checkout.process_order",
                attributes={
                    "sentry.op": "code.block"
                }
            ):
                if len(quantities) == 0:
                    raise Exception("Invalid checkout request: cart is empty")

                quantities = {int(k): v for k, v in cart['quantities'].items()}
                inventory_dict = {x.productid: x for x in inventory}
                for product_id in quantities:
                    inventory_count = inventory_dict[product_id].count if product_id in inventory_dict else 0
                    if inventory_count >= quantities[product_id]:
                        decrement_inventory(inventory_dict[product_id].id, quantities[product_id])
                        fulfilled_count += 1
                    else:
                        title = list(filter(lambda x: x['id'] == product_id, cart['items']))[0]['title']
                        out_of_stock.append(title)
    except Exception as err:

        logger.error('Failed to validate inventory with cart: %s', cart)
        raise Exception("Error validating enough inventory for product") from err

    if len(out_of_stock) == 0:
        result = {'status': 'success'}
        logging.info("Checkout successful")
    else:
        # react doesn't handle these yet, shows "Checkout complete" as long as it's HTTP 200
        if fulfilled_count == 0:
            result = {'status': 'failed'} # All items are out of stock
        else:
            result = {'status': 'partial', 'out_of_stock': out_of_stock}

    return make_response(json.dumps(result))


@app.route('/success', methods=['GET'])
def success():
    logger.info('Received /success endpoint request')


    logger.info('Completed /success request')
    return "success from flask"


@app.route('/products', methods=['GET'])
def products():
    logger.info('Received /products endpoint request')

    cache_key = str(random.randrange(100))

    product_inventory = None
    fetch_promotions = request.args.get('fetch_promotions')
    in_stock_only = request.args.get('in_stock_only')
    timeout_seconds = (EXTREMELY_SLOW_PROFILE if fetch_promotions else NORMAL_SLOW_PROFILE)

    logger.info('Processing /products')

    # Adding 0.5 seconds to the ruby /api_request in order to show caching
    # However, we want to keep the total trace time the same to preserve web vitals (+ other) functionality in sentry
    # Cache hits should keep the current delay, while cache misses will move 0.5 over to the ruby span
    ruby_delay_time = 0
    if (cache_key != "7"):
        timeout_seconds -= 0.5
        ruby_delay_time = 0.5

    try:
        logger.info('Processing /products - calling get_products()')
        with tracer.start_as_current_span(
            "products.get_and_process_products",
            attributes={
                "sentry.op": "code.block"
            }
        ):
            rows = get_products()

            if RUN_SLOW_PROFILE:
                start_time = time.time()
                productsJSON = json.loads(rows)
                descriptions = [product["description"] for product in productsJSON]
                with tracer.start_as_current_span(
                    "/get_iterator",
                    attributes={
                        "sentry.op": "code.block"
                    }
                ):
                    loop = get_iterator(len(descriptions) * 6 + (2 if fetch_promotions else -1))

                    for i in range(loop * 10):
                        time_delta = time.time() - start_time
                        if time_delta > timeout_seconds:
                            break

                        for i, description in enumerate(descriptions):
                            for pest in pests:
                                if in_stock_only and productsJSON[i] not in product_inventory:
                                    continue
                                if pest in description:
                                    try:
                                        del productsJSON[i:i + 1]
                                    except:
                                        productsJSON = json.loads(rows)
    except Exception as err:
        logger.error('Processing /products - error occurred')
        raise (err)

    logger.info('Completed /products request')


    get_api_response_with_caching(cache_key, ruby_delay_time)

    return rows

@tracer.start_as_current_span(name="get_api_response_with_caching")
def get_api_response_with_caching(key, delay):
    start_time = time.time()
    logger.info('Processing /products - starting API request')

    cached_response = redis_client.get("ruby.api.cache:" + str(key))

    if cached_response is not None:
        logger.info('Processing /products - cache hit for API request')

        return cached_response

    logger.info('Processing /products - cache miss for API request')


    try:
        with tracer.start_as_current_span(
            "call_api_on_cache_miss",
            attributes={
                "sentry.op": "code.block"
            }
        ):
            headers = parseHeaders(RUBY_CUSTOM_HEADERS, request.headers)
            r = requests.get(BACKEND_URL_RUBYONRAILS + "/api", headers=headers)
            r.raise_for_status()  # returns an HTTPError object if an error has occurred during the process

            time_delta = time.time() - start_time
            sleep_time = delay - time_delta
            if sleep_time > 0:
                time.sleep(sleep_time)

            # For demo show we want to show cache misses so only save 1 / 100
            if key == 7:
                logger.info('Processing /products - caching API response')
                redis_client.set("ruby.api.cache:" + str(key), key)

    except Exception as err:
        logger.error('Processing /products - API request failed')

    return key


@app.route('/products-join', methods=['GET'])
def products_join():
    logger.info('Received /products-join endpoint request')

    try:
        rows = get_products_join()
        logger.info('Processing /products-join - data retrieved')
    except Exception as err:
        logger.warn('Processing /products-join - error getting data')
        raise (err)

    try:
        headers = parseHeaders(RUBY_CUSTOM_HEADERS, request.headers)
        r = requests.get(BACKEND_URL_RUBYONRAILS + "/api", headers=headers)
        r.raise_for_status()  # returns an HTTPError object if an error has occurred during the process
        logger.info('Processing /products-join - backend API call successful')
    except Exception as err:
        logger.error('Processing /products-join - backend API call failed')

    return rows


@app.route('/api', methods=['GET'])
def api():
    logger.info('Received /api endpoint request')
    return "flask /api"


@app.route('/organization', methods=['GET'])
@cache.cached(timeout=1000, key_prefix="flask.cache.organization")
def organization():
    logger.info('Received /organization endpoint request')

    # perform get_products db query 1% of time in order
    #   to populate "Found In" endpoints in Queries
    if random.random() < 0.01:
        logger.info('Processing /organization - executing random products query')
        rows = get_products()
    return "flask /organization"


@app.route('/connect', methods=['GET'])
def connect():
    logger.info('Received /connect endpoint request')
    return "flask /connect"


@app.route('/apply-promo-code', methods=['POST'])
def apply_promo_code():
    logger.info('[/apply-promo-code] request received')

    try:
        body = json.loads(request.data)
        promo_code = body.get('value', '').strip()
        
        if not promo_code:
            logger.warning('[/apply-promo-code] bad request - missing value parameter')
            return '', 400
        
        promo_code_data = get_promo_code(promo_code)
        
        if not promo_code_data:
            logger.warning('[/apply-promo-code] code not found: %s', promo_code)
            return jsonify({
                "error": {
                    "code": "not_found",
                    "message": "Promo code not found."
                }
            }), 404
        
        promo_dict = dict(promo_code_data)
        logger.info('[/apply-promo-code] code found: %s', promo_dict)
        
        if promo_dict.get('expires_at') and promo_dict['expires_at'] <= datetime.now():
            logger.warning('[/apply-promo-code] code has expired: %s', promo_code)
            return jsonify({
                "error": {
                    "code": "expired",
                    "message": "Provided coupon code has expired."
                }
            }), 410 # Look what a clever HTTP response code! Good luck FE dev :D
        
        logger.info('[/apply-promo-code] valid code found: %s', promo_dict)
        
        return jsonify({
            "success": True,
            "promo_code": {
                "code": promo_dict['code'],
                "percent_discount": promo_dict['percent_discount'],
                "max_dollar_savings": promo_dict['max_dollar_savings']
            }
        }), 200
        
    except Exception as err:
        return '', 500


@app.route('/product/0/info', methods=['GET'])
def product_info():
    logger.info('Received /product/0/info endpoint request')

    time.sleep(.55)
    logger.info('Completed /product/0/info request')
    return "flask /product/0/info"



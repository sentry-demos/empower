import re
import os
import random
import requests
import time
import redis
import logging
from flask import Flask, json, jsonify, request, make_response, send_from_directory
from flask_cors import CORS
from openai import OpenAI
from flask_caching import Cache
from statsig.statsig_user import StatsigUser
from statsig import statsig, StatsigOptions, StatsigEnvironmentTier
import dotenv
from .db import get_products, get_products_join, get_inventory
from .utils import parseHeaders, get_iterator, evaluate_statsig_flags
from .queues.tasks import sendEmail
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
from sentry_sdk.integrations.redis import RedisIntegration
from sentry_sdk.integrations.logging import LoggingIntegration
from sentry_sdk.ai.monitoring import ai_track
from sentry_sdk.integrations.statsig import StatsigIntegration
from celery import Celery, states
from celery.exceptions import Ignore

RUBY_CUSTOM_HEADERS = ['se', 'customerType', 'email']
pests = ["aphids", "thrips", "spider mites", "lead miners", "scale", "whiteflies", "earwigs", "cutworms", "mealybugs",
         "fungus gnats"]

RELEASE = None
DSN = None
ENVIRONMENT = None
RUBY_BACKEND = None
RUN_SLOW_PROFILE = None

NORMAL_SLOW_PROFILE = 2 # seconds
EXTREMELY_SLOW_PROFILE = 24


def before_send(event, hint):
    # 'se' tag may have been set in app.before_request
    se = None
    if 'tags' in event.keys() and 'se' in event['tags']:
        se = event['tags']['se']

    if se not in [None, "undefined"]:
        se_tda_prefix_regex = r"[^-]+-tda-[^-]+-"
        se_fingerprint = se
        prefix = re.findall(se_tda_prefix_regex, se)
        if prefix:
            # Now that TDA puts platform/browser and test path into SE tag we want to prevent
            # creating separate issues for those. See https://github.com/sentry-demos/empower/pull/332
            se_fingerprint = prefix[0]

        if se.startswith('prod-tda-'):
            event['fingerprint'] = ['{{ default }}', se_fingerprint, RELEASE]
        else:
            event['fingerprint'] = ['{{ default }}', se_fingerprint]

    return event


def traces_sampler(sampling_context):
    sentry_sdk.set_context("sampling_context", sampling_context)
    wsgi_environ = sampling_context.get('wsgi_environ', {})
    REQUEST_METHOD = wsgi_environ.get('REQUEST_METHOD', 'GET')
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

        logging.info("> DSN %s", DSN)
        logging.info("> RELEASE %s", RELEASE)
        logging.info("> ENVIRONMENT %s", ENVIRONMENT)

        sentry_sdk.init(
            dsn=DSN,
            release=RELEASE,
            environment=ENVIRONMENT,
            enable_logs=True,
            integrations=[
                FlaskIntegration(),
                SqlalchemyIntegration(),
                RedisIntegration(cache_prefixes=["flask.", "ruby."]),

                StatsigIntegration()
            ],
            traces_sample_rate=1.0,
            before_send=before_send,
            traces_sampler=traces_sampler,
            _experiments={
                "enable_metrics": True,
                "profiles_sample_rate": 1.0,
            }
        )

        # Configure logging to work with Sentry
        logging.basicConfig(level=logging.INFO)

        super(MyFlask, self).__init__(import_name, *args, **kwargs)


app = MyFlask(__name__)
CORS(app)

# Create structured logger for this module
logger = logging.getLogger(__name__)

statsig.initialize(os.environ.get("STATSIG_SERVER_KEY"))

redis_host = os.environ.get("FLASK_REDISHOST", "localhost")
redis_port = int(os.environ.get("FLASK_LOCAL_REDISPORT", 6379))

cache_config = {
    "DEBUG": True,
    "CACHE_TYPE": "RedisCache",
    "CACHE_DEFAULT_TIMEOUT": 300,
    "CACHE_REDIS_HOST": redis_host,
    "CACHE_REDIS_PORT": redis_port,
    "CACHE_KEY_PREFIX": None
}

app.config.from_mapping(cache_config)
cache = Cache(app)

redis_client = redis.Redis(host=redis_host, port=redis_port, decode_responses=True)

@app.route('/enqueue', methods=['POST'])
def enqueue():
    logger.info('Received /enqueue endpoint request', extra={
        'endpoint': '/enqueue',
        'method': 'POST'
    })

    body = json.loads(request.data)
    email = body['email']
    r = sendEmail.apply_async(args=[email], queue='celery-new-subscriptions')

    logger.info('Completed /enqueue request - email task enqueued', extra={
        'task_id': r.task_id,
        'email': email,
        'queue': 'celery-new-subscriptions'
    })

    logging.info("task id: %s for email: %s", r.task_id, email)
    return jsonify({"status": "success"}), 200


@app.route('/suggestion', methods=['GET'])
def suggestion():
  logger.info('Received /suggestion endpoint request', extra={
      'endpoint': '/suggestion',
      'method': 'GET'
  })

  logging.info("got suggestion request")
  client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
  sentry_sdk.metrics.incr(
        key="endpoint_call",
        value=1,
        tags={"endpoint": "/suggestion", "method": "GET"},
    )

  catalog = request.args.get('catalog')
  geo = request.args.get('geo')

  logger.info('Processing /suggestion - starting AI pipeline', extra={
      'has_catalog': catalog is not None,
      'has_geo': geo is not None,
      'catalog_length': len(catalog) if catalog else 0
  })

  prompt = f'''You are witty plant salesman. Here is your catalog of plants: {catalog}.
    Provide a suggestion based on the user\'s location. Pick one plant from the catalog provided.
    Keep your response short and concise. Try to incorporate the weather and current season.'''

  @ai_track("Suggestion Pipeline")
  def suggestion_pipeline():
    with sentry_sdk.start_transaction(op="Suggestion AI", description="Suggestion ai pipeline"):
      response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=
        [
          { "role" : "system", "content": prompt },
          { "role": "user", "content": geo }
        ]).choices[0].message.content
      return response

  response = suggestion_pipeline()

  logger.info('Completed /suggestion request - AI suggestion generated', extra={
      'response_length': len(response) if response else 0
  })

  return jsonify({"suggestion": response}), 200


@app.route('/checkout', methods=['POST'])
def checkout():
    logger.info('Received /checkout endpoint request', extra={
        'endpoint': '/checkout',
        'method': 'POST'
    })

    logging.info("got checkout request")
    sentry_sdk.metrics.incr(
        key="endpoint_call",
        value=1,
        tags={"endpoint": "/checkout", "method": "POST"},
    )

    try:
        evaluate_statsig_flags()
    except Exception as e:
        sentry_sdk.capture_exception(e)
        logger.error('Error evaluating Statsig flags', extra={
            'error': str(e),
            'endpoint': '/checkout'
        })
        logging.error("Error evaluating flags in /checkout: %s", e)

    order = json.loads(request.data)
    cart = order["cart"]
    form = order["form"]
    validate_inventory = True if "validate_inventory" not in order else order["validate_inventory"] == "true"

    logger.info('Processing /checkout - validating order details', extra={
        'has_cart': cart is not None,
        'has_form': form is not None,
        'validate_inventory': validate_inventory,
        'cart_items_count': len(cart.get('quantities', {})) if cart else 0
    })

    inventory = []
    try:
        with sentry_sdk.start_span(op="/checkout.get_inventory", description="function"):
            with sentry_sdk.metrics.timing(key="checkout.get_inventory.execution_time"):
                inventory = get_inventory(cart)
    except Exception as err:
        logger.error('Failed to get inventory', extra={
            'error': str(err),
            'cart': str(cart)
        })
        raise (err)

    logging.info("> /checkout inventory %s", inventory)
    logging.info("> validate_inventory %s", validate_inventory)

    logger.info('Processing /checkout - inventory retrieved', extra={
        'inventory_count': len(inventory),
        'validate_inventory': validate_inventory
    })

    with sentry_sdk.start_span(op="process_order", description="function"):
        quantities = cart['quantities']
        for cartItem in quantities:
            for inventoryItem in inventory:
                logging.debug("> inventoryItem.count %s", inventoryItem['count'])
                if (validate_inventory and (inventoryItem.count < quantities[cartItem] or quantities[cartItem] >= inventoryItem.count)):
                    sentry_sdk.metrics.incr(key="checkout.failed")
                    logger.warning('Processing /checkout - insufficient inventory')
                    raise Exception('Not enough inventory for product')
        if len(inventory) == 0 or len(quantities) == 0:
            logger.error('Processing /checkout - empty inventory or quantities', extra={
                'inventory_length': len(inventory),
                'quantities_length': len(quantities)
            })
            raise Exception("Not enough inventory for product")

    logger.info('Completed /checkout request successfully', extra={
        'processed_items': len(quantities)
    })

    response = make_response("success")
    return response


@app.route('/success', methods=['GET'])
def success():
    logger.info('Received /success endpoint request', extra={
        'endpoint': '/success',
        'method': 'GET'
    })

    sentry_sdk.metrics.incr(
        key="endpoint_call",
        value=1,
        tags={"endpoint": "/success", "method": "GET"},
    )

    logger.info('Completed /success request')
    return "success from flask"


@app.route('/products', methods=['GET'])
def products():
    logger.info('Received /products endpoint request', extra={
        'endpoint': '/products',
        'method': 'GET'
    })

    sentry_sdk.metrics.incr(
        key="endpoint_call",
        value=1,
        tags={"endpoint": "/products", "method": "GET"},
    )
    cache_key = str(random.randrange(100))

    product_inventory = None
    fetch_promotions = request.args.get('fetch_promotions')
    in_stock_only = request.args.get('in_stock_only')
    timeout_seconds = (EXTREMELY_SLOW_PROFILE if fetch_promotions else NORMAL_SLOW_PROFILE)

    logger.info('Processing /products - request parameters', extra={
        'cache_key': cache_key,
        'fetch_promotions': fetch_promotions is not None,
        'in_stock_only': in_stock_only is not None,
        'timeout_seconds': timeout_seconds
    })

    # Adding 0.5 seconds to the ruby /api_request in order to show caching
    # However, we want to keep the total trace time the same to preserve web vitals (+ other) functionality in sentry
    # Cache hits should keep the current delay, while cache misses will move 0.5 over to the ruby span
    ruby_delay_time = 0
    if (cache_key != "7"):
        timeout_seconds -= 0.5
        ruby_delay_time = 0.5

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
        logger.error('Processing /products - error occurred', extra={
            'error': str(err),
            'cache_key': cache_key,
            'fetch_promotions': fetch_promotions,
            'in_stock_only': in_stock_only
        })
        sentry_sdk.capture_exception(err)
        raise (err)

    logger.info('Completed /products request', extra={
        'cache_key': cache_key,
        'ruby_delay_time': ruby_delay_time
    })

    logging.info("cache_key: %s", cache_key)
    # get_api_request(cache_key, ruby_delay_time)

    return rows


def get_api_request(key, delay):
    start_time = time.time()
    logger.info('Processing /products - starting API request', extra={
        'cache_key': str(key),
        'delay': delay
    })

    with sentry_sdk.start_span(op="/ruby_cached_api_request", description="function"):
      cached_response = redis_client.get("ruby.api.cache:" + str(key))

      if cached_response is not None:
          logger.info('Processing /products - cache hit for API request', extra={
              'cache_key': str(key)
          })
          logging.info("> cache hit: %s", key)
          return cached_response

      logger.info('Processing /products - cache miss for API request', extra={
          'cache_key': str(key)
      })
      logging.info("> cache miss: %s", key)

      try:
          with sentry_sdk.start_span(op="/api_request", description="function"):
              headers = parseHeaders(RUBY_CUSTOM_HEADERS, request.headers)
              r = requests.get(RUBY_BACKEND + "/api", headers=headers)
              r.raise_for_status()  # returns an HTTPError object if an error has occurred during the process

              time_delta = time.time() - start_time
              sleep_time = delay - time_delta
              if sleep_time > 0:
                time.sleep(sleep_time)

              # For demo show we want to show cache misses so only save 1 / 100
              if key == 7:
                logger.info('Processing /products - caching API response', extra={
                    'cache_key': str(key)
                })
                redis_client.set("ruby.api.cache:" + str(key), key)

      except Exception as err:
          logger.error('Processing /products - API request failed', extra={
              'error': str(err),
              'cache_key': str(key),
              'ruby_backend': RUBY_BACKEND
          })
          sentry_sdk.capture_exception(err)

      return key


@app.route('/products-join', methods=['GET'])
def products_join():
    logger.info('Received /products-join endpoint request', extra={
        'endpoint': '/products-join',
        'method': 'GET'
    })

    try:
        with sentry_sdk.start_span(op="/products-join.get_products_join", description="function"):
            rows = get_products_join()
            logger.info('Processing /products-join - data retrieved', extra={
                'rows_count': len(rows) if rows else 0
            })
    except Exception as err:
        logger.error('Processing /products-join - error getting data', extra={
            'error': str(err)
        })
        sentry_sdk.capture_exception(err)
        raise (err)

    try:
        headers = parseHeaders(RUBY_CUSTOM_HEADERS, request.headers)
        r = requests.get(RUBY_BACKEND + "/api", headers=headers)
        r.raise_for_status()  # returns an HTTPError object if an error has occurred during the process
        logger.info('Processing /products-join - backend API call successful', extra={
            'status_code': r.status_code,
            'backend_url': RUBY_BACKEND + "/api"
        })
    except Exception as err:
        logger.error('Processing /products-join - backend API call failed', extra={
            'error': str(err),
            'backend_url': RUBY_BACKEND + "/api"
        })
        sentry_sdk.capture_exception(err)

    return rows


@app.route('/handled', methods=['GET'])
def handled_exception():
    logger.info('Received /handled endpoint request', extra={
        'endpoint': '/handled',
        'method': 'GET'
    })

    try:
        '2' + 2
    except Exception as err:
        logger.error('Processing /handled - intentional exception occurred', extra={
            'error': str(err),
            'error_type': type(err).__name__
        })
        sentry_sdk.capture_exception(err)
    return 'failed'


@app.route('/unhandled', methods=['GET'])
def unhandled_exception():
    logger.info('Received /unhandled endpoint request', extra={
        'endpoint': '/unhandled',
        'method': 'GET'
    })

    obj = {}
    obj['keyDoesnt  Exist']


@app.route('/api', methods=['GET'])
def api():
    logger.info('Received /api endpoint request', extra={
        'endpoint': '/api',
        'method': 'GET'
    })
    return "flask /api"


@app.route('/organization', methods=['GET'])
@cache.cached(timeout=1000, key_prefix="flask.cache.organization")
def organization():
    logger.info('Received /organization endpoint request', extra={
        'endpoint': '/organization',
        'method': 'GET'
    })

    # perform get_products db query 1% of time in order
    #   to populate "Found In" endpoints in Queries
    if random.random() < 0.01:
        logger.info('Processing /organization - executing random products query', extra={
            'probability_threshold': 0.01
        })
        rows = get_products()
    return "flask /organization"


@app.route('/connect', methods=['GET'])
def connect():
    logger.info('Received /connect endpoint request', extra={
        'endpoint': '/connect',
        'method': 'GET'
    })
    return "flask /connect"


@app.route('/showSuggestion', methods=['GET'])
def showSuggestion():
    logger.info('Received /showSuggestion endpoint request', extra={
        'endpoint': '/showSuggestion',
        'method': 'GET'
    })

    has_openai_key = os.getenv("OPENAI_API_KEY") is not None
    logger.info('Processing /showSuggestion - OpenAI key availability checked', extra={
        'has_openai_key': has_openai_key
    })

    return jsonify({"response": has_openai_key}), 200

@app.route('/product/0/info', methods=['GET'])
def product_info():
    logger.info('Received /product/0/info endpoint request', extra={
        'endpoint': '/product/0/info',
        'method': 'GET',
        'sleep_duration': 0.55
    })

    time.sleep(.55)
    logger.info('Completed /product/0/info request')
    return "flask /product/0/info"


# uncompressed assets
@app.route('/uncompressed_assets/<path:path>')
def send_report(path):
    logger.info('Received /uncompressed_assets request', extra={
        'endpoint': '/uncompressed_assets',
        'file_path': path,
        'sleep_duration': 0.55
    })

    time.sleep(.55)
    response = send_from_directory('../uncompressed_assets', path)
    # `Timing-Allow-Origin: *` allows timing/sizes to visbile in span
    response.headers['Timing-Allow-Origin'] = '*'
    # Overwriting `Content-Type` header to disable compression
    response.headers['Content-Type'] = 'application/octet-stream'

    logger.info('Completed /uncompressed_assets request', extra={
        'file_path': path,
        'content_type': 'application/octet-stream'
    })

    return response


# compressed assets
@app.route('/compressed_assets/<path:path>')
def send_report_configured_properly(path):
    logger.info('Received /compressed_assets request', extra={
        'endpoint': '/compressed_assets',
        'file_path': path
    })

    response = send_from_directory('../compressed_assets', path)
    # `Timing-Allow-Origin: *` allows timing/sizes to visbile in span
    response.headers['Timing-Allow-Origin'] = '*'

    logger.info('Completed /compressed_assets request', extra={
        'file_path': path
    })

    return response


@app.before_request
def sentry_event_context():
    # Extract context information
    se = request.headers.get('se')
    customerType = request.headers.get('customerType')
    email = request.headers.get('email')

    # Log request context information
    logger.debug('Setting up request context', extra={
        'endpoint': request.endpoint,
        'method': request.method,
        'has_se_header': se is not None and se != "undefined",
        'has_customer_type': customerType is not None and customerType != "undefined",
        'has_email': email is not None and email != "undefined"
    })

    if se not in [None, "undefined"]:
        sentry_sdk.set_tag("se", se)
    else:
        # sometimes this is the only way to propagate, e.g. when requested through a dynamically
        # inserted HTML tag as in case with (un)compressed_assets
        se = request.args.get('se')
        if se not in [None, "undefined"]:
            sentry_sdk.set_tag("se", se)

    if customerType not in [None, "undefined"]:
        sentry_sdk.set_tag("customerType", customerType)

    if email not in [None, "undefined"]:
        sentry_sdk.set_user({"email": email})

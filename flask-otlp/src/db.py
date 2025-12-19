import json
import operator
import os
import logging
import sentry_sdk
import sqlalchemy
from sqlalchemy import create_engine, text
from .utils import weighter
from dotenv import load_dotenv
from opentelemetry import trace
load_dotenv()

# Get OpenTelemetry tracer
tracer = trace.get_tracer(__name__)

HOST = os.environ["DB_HOST"]
DATABASE = os.environ["DB_DATABASE"]
USERNAME = os.environ["DB_USERNAME"]
PASSWORD = os.environ["DB_PASSWORD"]
FLASKOTLP_ENVIRONMENT = os.environ["FLASKOTLP_ENVIRONMENT"]
PRODUCTS_NUM = 4

class DatabaseConnectionError (Exception):
    pass


if FLASKOTLP_ENVIRONMENT == "local":
    print("> ENVIRONMENT local ")
    db = create_engine('postgresql://' + USERNAME + ':' + PASSWORD + '@' + HOST + ':5432/' + DATABASE)
else:
    CLOUD_SQL_CONNECTION_NAME = os.environ["DB_CLOUD_SQL_CONNECTION_NAME"]
    print("> ENVIRONMENT production ")
    print("> CLOUD_SQL_CONNECTION_NAME", CLOUD_SQL_CONNECTION_NAME)
    db = sqlalchemy.create_engine(
        sqlalchemy.engine.url.URL(
            drivername='postgresql+pg8000',
            username=USERNAME,
            password=PASSWORD,
            database=DATABASE,
            query={
                'unix_sock': '/cloudsql/{}/.s.PGSQL.5432'.format(CLOUD_SQL_CONNECTION_NAME)
            }
        )
    )

# N+1 because a sql query for every product n
@tracer.start_as_current_span(name="get_products")
def get_products():
    results = []
    try:
        connection = db.connect()

        n = weighter(operator.le, 12)
        # adjust by number of products to get the same timeout as we had in the past
        # before pg_sleep() was moved out of SELECT clause.
        n *= PRODUCTS_NUM
        query = text("SELECT * FROM products WHERE id IN (SELECT id from products, pg_sleep(:sleep_duration))")
        products = connection.execute(query, sleep_duration=n).fetchall()

        for product in products:
            # product_bundles is a "sleepy view", run the following query to get current sleep duration:
            # SELECT pg_get_viewdef('product_bundles', true)
            query = text("SELECT * FROM reviews, product_bundles WHERE productId = :x")
            reviews = connection.execute(query, x=product.id).fetchall()

            result = dict(product)
            result["reviews"] = []

            for review in reviews:
                result["reviews"].append(dict(review))
            results.append(result)

        with tracer.start_as_current_span(
            "get_products.combined_reviews.json",
            attributes={
                "sentry.op": "serialization"
            }
        ):
            result = json.dumps(results, default=str)
        return result
    except Exception as err:
        raise DatabaseConnectionError('get_products') from err

# 2 sql queries max, then sort in memory
@tracer.start_as_current_span(name="get_products_join")
def get_products_join():
    results = []
    try:
        with tracer.start_as_current_span(
            "get_products_join",
            attributes={
                "db.system": "postgresql",
                "db.operation": "connect"
            }
        ):
            connection = db.connect()

        with tracer.start_as_current_span(
            "get_products_join",
            attributes={
                "db.system": "postgresql",
                "db.operation": "query",
                "db.statement": "SELECT * FROM products"
            }
        ) as span:
            products = connection.execute(
                "SELECT * FROM products"
            ).fetchall()
            span.set_attribute("totalProducts",len(products))
            span.set_attribute("products",str(products))

        with tracer.start_as_current_span(
            "get_products_join.reviews",
            attributes={
                "db.system": "postgresql",
                "db.operation": "query",
                "db.statement": "SELECT reviews.id, products.id AS productid..."
            }
        ) as span:
            reviews = connection.execute(
                "SELECT reviews.id, products.id AS productid, reviews.rating, reviews.customerId, reviews.description, reviews.created FROM reviews INNER JOIN products ON reviews.productId = products.id"
            ).fetchall()
            span.set_attribute("reviews",str(reviews))
    except Exception as err:
        raise DatabaseConnectionError('get_products_join') from err

    with tracer.start_as_current_span(
        "get_products_join.format_results",
        attributes={
            "sentry.op": "code.block"
        }
    ) as span:
        for product in products:
            result = dict(product)
            result["reviews"] = []

            for review in reviews:
                productId=review[1]
                if productId == product["id"]:
                    result["reviews"].append(dict(review))
            results.append(result)
        span.set_attribute("results", str(results))

    with tracer.start_as_current_span(
        "joined_reviews.json",
        attributes={
            "sentry.op": "serialization"
        }
    ):
        result = json.dumps(results, default=str)

    return result

@tracer.start_as_current_span(name="get_inventory")
def get_inventory(cart):
    print("> get_inventory")

    quantities = cart['quantities']

    print("> quantities", quantities)

    productIds = []
    for productId_str in quantities.keys():
        logging.info(f"Processing product ID: {productId_str}")
        productIds.append(int(productId_str))

    print("> productIds", productIds)

    try:
        connection = db.connect()
        # Use parameterized query with ANY() to safely handle array of product IDs
        query = text("SELECT * FROM inventory WHERE productId = ANY(:product_ids)")
        inventory = connection.execute(query, product_ids=productIds).fetchall()
        trace.get_current_span().set_attribute("inventory", str(inventory))
    except Exception as err:
        raise DatabaseConnectionError('get_inventory') from err

    return inventory

def decrement_inventory(id, count):
    pass

@tracer.start_as_current_span(name="get_promo_code")
def get_promo_code(code):
    """Get promo code from database by code string"""
    try:
        with tracer.start_as_current_span(
            "get_promo_code",
            attributes={
                "db.system": "postgresql",
                "db.operation": "connect"
            }
        ):
            connection = db.connect()
        
        with tracer.start_as_current_span(
            "get_promo_code",
            attributes={
                "db.system": "postgresql",
                "db.operation": "query",
                "db.statement": "SELECT * FROM promo_codes WHERE code = :code AND is_active = true"
            }
        ) as span:
            query = text("SELECT * FROM promo_codes WHERE code = :code AND is_active = true")
            result = connection.execute(query, code=code).fetchone()
            span.set_attribute("promo_code", str(result))
        
        return result
    except Exception as err:
        raise DatabaseConnectionError('get_promo_code') from err

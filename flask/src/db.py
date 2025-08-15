import json
import operator
import os
import logging
import sentry_sdk
import sqlalchemy
from sqlalchemy import create_engine, text
from .utils import weighter
from dotenv import load_dotenv
load_dotenv()

HOST = os.environ["DB_HOST"]
DATABASE = os.environ["DB_DATABASE"]
USERNAME = os.environ["DB_USERNAME"]
PASSWORD = os.environ["DB_PASSWORD"]
FLASK_ENV = os.environ["FLASK_ENV"]
PRODUCTS_NUM = 4

class DatabaseConnectionError (Exception):
    pass


if FLASK_ENV == "test":
    print("> ENVIRONMENT test ")
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

# Fixed N+1 query issue by using JOIN instead of loop
def get_products():
    results = []
    try:
        with sentry_sdk.start_span(op="get_products", description="db.connect"):
            connection = db.connect()

        n = weighter(operator.le, 12)
        # adjust by number of products to get the same timeout as we had in the past
        # before pg_sleep() was moved out of SELECT clause.
        n *= PRODUCTS_NUM
        query = text("SELECT * FROM products WHERE id IN (SELECT id from products, pg_sleep(:sleep_duration))")
        products = connection.execute(query, sleep_duration=n).fetchall()

        # Get all reviews and product_bundles data in a single query
        # This eliminates the N+1 query pattern by mimicking the original cross join behavior
        # Original query was: SELECT * FROM reviews, product_bundles WHERE productId = :x
        # This is equivalent to a cross join between reviews and product_bundles for each product
        product_ids = [product.id for product in products]
        
        if product_ids:
            query = text("""
                SELECT r.*, pb.*
                FROM reviews r, product_bundles pb 
                WHERE r.productId = pb.productId 
                AND r.productId = ANY(:product_ids)
            """)
            reviews_data = connection.execute(query, product_ids=product_ids).fetchall()
        else:
            reviews_data = []

        # Create a dictionary to group reviews by product_id for efficient lookup
        reviews_by_product = {}
        for row in reviews_data:
            product_id = row.productId  # Use the productId from reviews table
            if product_id not in reviews_by_product:
                reviews_by_product[product_id] = []
            reviews_by_product[product_id].append(dict(row))

        # Build results using the pre-fetched review data
        for product in products:
            result = dict(product)
            result["reviews"] = reviews_by_product.get(product.id, [])
            results.append(result)

        with sentry_sdk.start_span(op="serialization", description="json"):
            result = json.dumps(results, default=str)
        return result
    except Exception as err:
        raise DatabaseConnectionError('get_products') from err

# 2 sql queries max, then sort in memory
def get_products_join():
    results = []
    try:
        with sentry_sdk.start_span(op="get_products_join", description="db.connect"):
            connection = db.connect()

        with sentry_sdk.start_span(op="get_products_join", description="db.query") as span:
            products = connection.execute(
                "SELECT * FROM products"
            ).fetchall()
            span.set_tag("totalProducts",len(products))
            span.set_data("products",products)

        with sentry_sdk.start_span(op="get_products_join.reviews", description="db.query") as span:
            reviews = connection.execute(
                "SELECT reviews.id, products.id AS productid, reviews.rating, reviews.customerId, reviews.description, reviews.created FROM reviews INNER JOIN products ON reviews.productId = products.id"
            ).fetchall()
            span.set_data("reviews",reviews)
    except Exception as err:
        raise DatabaseConnectionError('get_products_join') from err

    with sentry_sdk.start_span(op="get_products_join.format_results", description="function") as span:
        for product in products:
            result = dict(product)
            result["reviews"] = []

            for review in reviews:
                productId=review[1]
                if productId == product["id"]:
                    result["reviews"].append(dict(review))
            results.append(result)
        span.set_data("results", results)

    with sentry_sdk.start_span(op="serialization", description="json"):
        result = json.dumps(results, default=str)

    return result

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
        with sentry_sdk.start_span(op="get_inventory", description="db.connect"):
            connection = db.connect()
        with sentry_sdk.start_span(op="get_inventory", description="db.query") as span:
            # Use parameterized query with ANY() to safely handle array of product IDs
            query = text("SELECT * FROM inventory WHERE productId = ANY(:product_ids)")
            inventory = connection.execute(query, product_ids=productIds).fetchall()
            span.set_data("inventory",inventory)
    except Exception as err:
        raise DatabaseConnectionError('get_inventory') from err

    return inventory

def decrement_inventory(id, count):
    pass

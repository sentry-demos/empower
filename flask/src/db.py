import json
import operator
import os
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

# error type was 'Error' so using the error message here so it's more specific
UNPACK_FROM_ERROR="unpack_from requires a buffer of at least 5 bytes for unpacking 5 bytes at offset"

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

# N+1 because a sql query for every product n
def get_products():
    results = []
    try:
        with sentry_sdk.start_span(op="get_products", description="db.connect"):
            connection = db.connect()

        n = weighter(operator.le, 12)
        # adjust by number of products to get the same timeout as we had in the past
        # before pg_sleep() was moved out of SELECT clause.
        n *= PRODUCTS_NUM
        products = connection.execute(
            "SELECT * FROM products WHERE id IN (SELECT id from products, pg_sleep(%s))" % (n)
        ).fetchall()

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

        with sentry_sdk.start_span(op="serialization", description="json"):
            result = json.dumps(results, default=str)
        return result
    except BrokenPipeError as err:
        raise DatabaseConnectionError('get_products')
    except Exception as err:
        err_string = str(err)
        if UNPACK_FROM_ERROR in err_string:
            raise DatabaseConnectionError('get_products')
        else:
            raise(err)

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
    except BrokenPipeError as err:
        raise DatabaseConnectionError('get_products_join')
    except Exception as err:
        err_string = str(err)
        if UNPACK_FROM_ERROR in err_string:
            raise DatabaseConnectionError('get_products_join')
        else:
            raise(err)

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

    product_ids = list(quantities.keys())
    if not product_ids:
        return []

    productIds = formatArray(product_ids)
    print("> productIds", productIds)

    try:
        with sentry_sdk.start_span(op="get_inventory", description="db.connect"):
            connection = db.connect()
        with sentry_sdk.start_span(op="get_inventory", description="db.query") as span:
            inventory = connection.execute(
                "SELECT * FROM inventory WHERE productId in %s" % (productIds)
            ).fetchall()
            span.set_data("inventory",inventory)
    except BrokenPipeError as err:
        raise DatabaseConnectionError('get_inventory')
    except Exception as err:
        err_string = str(err)
        if UNPACK_FROM_ERROR in err_string:
            raise DatabaseConnectionError('get_inventory')
        else:
            raise(err)

    return inventory



def formatArray(ids):
    numbers = ""
    for _id in ids:
        numbers += (str(_id) + ",") # Ensure ID is string
    output = "(" + numbers[:-1] + ")"
    return output

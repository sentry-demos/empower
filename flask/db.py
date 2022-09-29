import json
import operator
import os
import sentry_sdk
import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.sql import text
from utils import weighter
from dotenv import load_dotenv
load_dotenv()

HOST = os.getenv("HOST")
DATABASE = os.getenv("DATABASE")
USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")
FLASK_ENV = os.environ.get("FLASK_ENV")
CLOUD_SQL_CONNECTION_NAME = os.environ.get("CLOUD_SQL_CONNECTION_NAME")

class DatabaseConnectionError (Exception):
    pass

# error type was 'Error' so using the error message here so it's more specific
UNPACK_FROM_ERROR="unpack_from requires a buffer of at least 5 bytes for unpacking 5 bytes at offset"

if FLASK_ENV == "test":
    print("> ENVIRONMENT test ")
    db = create_engine('postgresql://' + USERNAME + ':' + PASSWORD + '@' + HOST + ':5432/' + DATABASE)
else:
    print("> ENVIRONMENT production ")
    print("> CLOUD_SQL_CONNECTION_NAME", CLOUD_SQL_CONNECTION_NAME)
    db = sqlalchemy.create_engine(
        sqlalchemy.engine.url.URL(
            drivername='postgres+pg8000',
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

        with sentry_sdk.start_span(op="get_products", description="db.query") as span:
            n = weighter(operator.le, 12)
            products = connection.execute(
                "SELECT *, pg_sleep(%s) FROM products" % (n)
            ).fetchall()
            print("> totalProducts %s" % len(products))
            span.set_tag("totalProducts",len(products))
            span.set_data("products",products)

        '''
        1. add products row SQL 1. gshell, select all, find directions, add 1, select all again, then step 2
        2. run it, see if reviews[] is blank in response to frontend
        3. add reviews for that new product
        4. run it, see if reviews[] are there in response to frontend
        '''
        
        with sentry_sdk.start_span(op="get_products.reviews", description="db.query") as span:
            for product in products:
                query = text("SELECT *, pg_sleep(0.0625) FROM reviews WHERE productId = :x")
                reviews = connection.execute(query, x=product.id).fetchall()

                result = dict(product)
                result["reviews"] = []

                for review in reviews:
                    result["reviews"].append(dict(review))
                results.append(result)
            span.set_data("reviews", results)

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

    productIds = []
    for productId in quantities:
        productIds.append(productId)

    productIds = formatArray(productIds)
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
        numbers += (_id + ",")
    output = "(" + numbers[:-1] + ")"
    return output
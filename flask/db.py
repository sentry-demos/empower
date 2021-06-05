import json
import os
import sentry_sdk
import sqlalchemy
from sqlalchemy import create_engine
from dotenv import load_dotenv
load_dotenv()

HOST = os.getenv("HOST")
DATABASE = os.getenv("DATABASE")
USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")
FLASK_ENV = os.environ.get("FLASK_ENV")
CLOUD_SQL_CONNECTION_NAME = os.environ.get("CLOUD_SQL_CONNECTION_NAME")

# TODO removed FLASK_ENV from .env.default, because passing it from run.sh. re-test all workflows.
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
        conn = db.connect()
        products = conn.execute(
            "SELECT * FROM products"
        ).fetchall()
        
        for product in products:
            reviews = conn.execute(
                "SELECT * FROM reviews WHERE productId = {}".format(product.id)
            ).fetchall()
            result = dict(product)
            result["reviews"] = []

            for review in reviews:
                result["reviews"].append(dict(review))
            results.append(result)
        return json.dumps(results, default=str)
    except Exception as err:
        raise(err)

# 2 sql queries max, then sort in memory
def get_products_join():
    results = []
    try:
        conn = db.connect()
        products = conn.execute(
            "SELECT * FROM products"
        ).fetchall()

        reviews = conn.execute(
            "SELECT reviews.id, products.id AS productid, reviews.rating, reviews.customerId, reviews.description, reviews.created FROM reviews INNER JOIN products ON reviews.productId = products.id"
        ).fetchall()

        for product in products:
            result = dict(product)
            result["reviews"] = []

            for review in reviews:
                result["reviews"].append(dict(review))
            results.append(result)

        return json.dumps(results, default=str)
    except Exception as err:
        raise(err)

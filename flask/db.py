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

if FLASK_ENV == "test":
    print("> TEST ")
    db = create_engine('postgresql://' + USERNAME + ':' + PASSWORD + '@' + HOST + ':5432/' + DATABASE)
else:
    print("> PRODUCTION ")
    cloud_sql_connection_name = "sales-engineering-sf:us-central1:tracing-db-pg"
    db = sqlalchemy.create_engine(
        sqlalchemy.engine.url.URL(
            drivername='postgres+pg8000',
            username=USERNAME,
            password=PASSWORD,
            database=DATABASE,
            query={
                'unix_sock': '/cloudsql/{}/.s.PGSQL.5432'.format(cloud_sql_connection_name)
            }
        )
    )

def get_products():
    tools = []
    try:
        conn = db.connect()

        products = conn.execute(
            "SELECT * FROM products"
        ).fetchall()
        
        # TODO
        # conn.close()

        response = []

        for product in products:
            print("> product.id", product.id)
            reviews = conn.execute(
                "SELECT * FROM reviews WHERE productId = {}".format(product.id)
            ).fetchall()
            print("> len(reviews)", len(reviews))
            response.append(dict(product))
        return json.dumps(response)
    except Exception as err:
        raise(err)

# def get_products_og():
#     tools = []
#     try:
#         # with sentry_sdk.start_span(op="connect to db"):
#         conn = db.connect()
#         # with sentry_sdk.start_span(op="run query"):
#             # wait(operator.le, 12, 1)
#         results = conn.execute(
#             "SELECT * FROM products"
#         ).fetchall()
#         conn.close()

#         rows = []
#         # with sentry_sdk.start_span(op="format results"):
#         for row in results:
#             rows.append(dict(row))
#         return json.dumps(rows)
#     except Exception as err:
#         raise(err)
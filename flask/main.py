import datetime
import os
import sys
# from flask import Flask, request, json, abort, make_response, jsonify
from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
load_dotenv()

## TODO util or rm this altogether, require always .env or shell script defined? TBD
RELEASE = None
if os.environ.get("RELEASE") is None:
    d=datetime.date.today()
    week=str((d.day-1)//7+1)
    date_given = datetime.datetime.today().date()
    month = str(date_given.month)
    RELEASE = month + "." + week
else:
    RELEASE = os.environ.get("RELEASE")
print("RELEASE is " + RELEASE)

DSN = os.getenv("FLASK_APP_DSN")
print("DSN", DSN)
def before_send(event, hint):
    # TODO need this still?
    if event['request']['method'] == 'OPTIONS':
        return null
    print("> event", event)
    return event

sentry_sdk.init(
    dsn= DSN,
    traces_sample_rate=1.0,
    integrations=[FlaskIntegration(), SqlalchemyIntegration()],
    release=RELEASE,
    environment="dev",
    before_send=before_send
)

app = Flask(__name__)
CORS(app)
 
@app.route('/success', methods=['GET'])
def success():    
    # print('/successs')
    return "successs"

@app.route('/products', methods=['GET'])
def products():    
    # print('/products')
    return "products"

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
        # sys.exit()
    # else:
        # print("it is", typeof(i.major))
    # This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app.
    app.run(host='127.0.0.1', port=8080, debug=True)
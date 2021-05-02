import sys
# import os
# from flask import Flask, request, json, abort, make_response, jsonify
from flask import Flask
from flask_cors import CORS
# from dotenv import load_dotenv
# from dotenv import load_dotenv
# import sentry_sdk
# from sentry_sdk.integrations.flask import FlaskIntegration
# load_dotenv()

# DSN = os.getenv("FLASK_APP_DSN")

# def before_send(event, hint):
#     if event['request']['method'] == 'OPTIONS':
#         return null
#     return event

# sentry_sdk.init(
#     dsn= DSN
#     traces_sample_rate=1.0,
#     integrations=[FlaskIntegration()],
#     release=RELEASE,
#     environment="production",
#     before_send=before_send
# )

app = Flask(__name__)
CORS(app)

@app.route('/success', methods=['GET'])
def success():    
    # print('/successs')
    # response = make_response("successs")
    return "successs"

@app.route('/products', methods=['GET'])
def products():    
    # print('/products')
    # response = make_response("productss")
    return "products"

if __name__ == '__main__':
    i = sys.version_info
    print(i.major)
    # if i.major != "3":
    if sys.version_info[0] < 3:
        raise SystemExit("Failed to start: need python3")
        # sys.exit()
    # else:
        # print("it is", typeof(i.major))
    # This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app.
    app.run(host='127.0.0.1', port=8080, debug=True)
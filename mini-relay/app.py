import flask

app = flask.Flask(__name__)


@app.post('/api/<p>/envelope/')
def envelope(p: str) -> flask.Response:
    # TODO: save out flask.request.data
    ret = app.make_response(('', 204))
    ret.access_control_allow_origin = '*'
    return ret

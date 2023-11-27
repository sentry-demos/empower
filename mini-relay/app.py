from __future__ import annotations

import flask

app = flask.Flask(__name__)


@app.post('/api/<p>/envelope/')
def envelope(p: str) -> flask.Response:
    # TODO: save out flask.request.data
    ret = app.make_response(('', 204))
    ret.access_control_allow_origin = '*'
    return ret


@app.post('/<path:path>')
def unhandled(path: str) -> tuple[str, int]:
    print('*' * 79)
    print(f'unhandled path: {path}')
    print('*' * 79)
    return '', 400

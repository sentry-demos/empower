from __future__ import annotations

import os
import gzip
import time

import flask

app = flask.Flask(__name__)


@app.post('/api/<p>/envelope/')
def envelope(p: str) -> flask.Response:
    if flask.request.headers.get('content-encoding', 'identity') == 'gzip':
        data = gzip.decompress(flask.request.data)
    else:
        data = flask.request.data

    os.makedirs(f'/data/{p}', exist_ok=True)
    with open(f'/data/{p}/{time.monotonic()}', 'wb') as f:
        f.write(data)

    ret = app.make_response(('', 204))
    ret.access_control_allow_origin = '*'
    return ret


@app.post('/<path:path>')
def unhandled(path: str) -> tuple[str, int]:
    print('*' * 79)
    print(f'unhandled path: {path}')
    print('*' * 79)
    return '', 400

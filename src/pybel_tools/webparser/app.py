import io
import time

import flask
import pybel.parser
from flask import Flask, request
from pyparsing import ParseException

app = Flask(__name__)

parser = pybel.parser.BelParser()
parser.statement.streamline()
app.config['GRAPH'] = parser


@app.route('/', methods=['GET'])
def no_place_like_home():
    return app.send_static_file('index.html')


@app.route('/parse/<statement>', methods=['GET', 'POST'])
def parse(statement):
    parser = app.config['GRAPH']
    parser.control_parser.clear()
    parser.control_parser.annotations.update({
        'added': str(time.asctime()),
        'ip': request.remote_addr,
        'host': request.host,
        'user': request.remote_user
    })
    parser.control_parser.annotations.update(request.args)
    res = parser.statement.parseString(statement)

    return flask.jsonify(**res.asDict())


@app.route('/dump')
def dump():
    out_stream = io.BytesIO()
    pybel.to_pickle(app.config['GRAPH'].graph, out_stream)
    return flask.Response(out_stream.getvalue(), mimetype='text/plain')


@app.route('/clear')
def clear():
    app.config['GRAPH'].clear()
    return "cleared"


if __name__ == '__main__':
    app.run()

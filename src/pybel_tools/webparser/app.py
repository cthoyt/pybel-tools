import io
import time

import flask
import pybel.parser
from flask import Flask, request

app = Flask(__name__)

parser = pybel.parser.BelParser()
parser.statement.setName('Relation Grammar')
parser.statement.streamline()
app.config['GRAPH'] = parser


@app.route('/', methods=['GET', 'POST'])
def no_place_like_home():
    return app.send_static_file('index.html')


@app.route('/parse/<statement>', methods=['GET', 'POST'])
def parse(statement):
    """Parses a statement that's been URL encoded. URL Parameters added as annotations to relation

    :param statement: a URL encoded BEL statement
    """
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
    """Dumps the content of the current graph as a PyBEL *.gpickle"""
    out_stream = io.BytesIO()
    pybel.to_pickle(app.config['GRAPH'].graph, out_stream)
    return flask.Response(out_stream.getvalue(), mimetype='text/plain')


@app.route('/clear')
def clear():
    """Clears the content of the current graph"""
    app.config['GRAPH'].clear()
    return "cleared"


if __name__ == '__main__':
    app.run()

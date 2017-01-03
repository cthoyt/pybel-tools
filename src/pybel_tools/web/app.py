import io
import logging
import time

import flask
from flask import Flask, request, redirect, flash
from flask_restless_swagger import SwagAPIManager as APIManager
from requests.utils import quote
from sqlalchemy.exc import IntegrityError
from werkzeug.utils import secure_filename

import pybel
import pybel.parser
from pybel.manager import models
from pybel.manager.cache import CacheManager
from pybel.manager.graph_cache import GraphCacheManager

ALLOWED_BEL_EXTENSIONS = {'bel'}
PARSER_RESOURCE_KEY = 'parser_resource_key'
CACHE_MANAGER = 'cache_manager'

log = logging.getLogger('pybel')
app = Flask(__name__)

cm = CacheManager()
models.Base.metadata.bind = cm.engine

manager = APIManager(app, session=cm.session)

manager.create_api(models.Network,
                   methods=['GET', 'POST'],
                   collection_name='network',
                   exclude_columns=['blob'])

manager.create_api(models.Namespace, methods=['GET', 'POST'],
                   collection_name='namespace',
                   exclude_columns=['entries'])

app.config[PARSER_RESOURCE_KEY] = pybel.parser.BelParser()
app.config[PARSER_RESOURCE_KEY].statement.streamline()


def allowed_file(filename, allowed_extensions):
    return '.' in filename and filename.rsplit('.', 1)[1] in allowed_extensions


@app.route('/', methods=['GET'])
def no_place_like_home():
    return app.send_static_file('index.html')


@app.route('/upload', methods=['GET', 'POST'])
def upload_bel():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)

        file = request.files['file']

        if not file.filename:
            flash('No selected file')
            return redirect(request.url)

        if file and allowed_file(file.filename, ALLOWED_BEL_EXTENSIONS):
            log.info('parsing from %s', secure_filename(file.filename))

            log_stream = io.StringIO()

            g = pybel.BELGraph(lines=(line.decode('utf-8') for line in file.stream), log_stream=log_stream)

            try:
                pybel.to_database(g)
            except IntegrityError as e:
                return 'Integrity Error: {}'.format(e)

            return '<!doctype html><html><body><h1>Parse Log</h1>' + '<br/>'.join(
                line for line in log_stream) + '</body></html>'

    return '''
<!doctype html>
<title>Upload new File</title>
<h1>Parse BEL File</h1>
<form action="/upload" method=post enctype=multipart/form-data>
    <p><input type=file name=file></p>
    <p><input type=submit value="Parse"></p>
</form>
'''


@app.route('/bel/', methods=['GET'])
def list_bel():
    gcm = GraphCacheManager()

    links = []

    fmt = '<tr><td><a href="/bel/{}">{}</a></td><td>{}</td></tr>'
    for name, version in gcm.ls():
        links.append(fmt.format(quote(name), name, version))

    html = '<html><h1>BEL Files</h1><table><tr><td>Document</td><td>Version</td></tr>' + "\n".join(
        links) + '</table></html>'
    return html


@app.route('/bel/<ns>', methods=['GET'])
def get_bel(ns):
    g = pybel.from_database(ns)
    return flask.Response(pybel.to_bel(g), mimetype='text/plain')


@app.route('/parser/parse/<statement>', methods=['GET', 'POST'])
def parse_bel(statement):
    parser = app.config[PARSER_RESOURCE_KEY]
    parser.control_parser.clear()
    parser.control_parser.annotations.update({
        'added': str(time.asctime()),
        'ip': request.remote_addr,
        'host': request.host,
        'user': request.remote_user
    })
    parser.control_parser.annotations.update(request.args)
    try:
        res = parser.statement.parseString(statement)
        return flask.jsonify(**res.asDict())
    except Exception as e:
        return "Exception: {}".format(e)


@app.route('/parser/dump')
def dump_bel():
    return flask.Response(pybel.to_bytes(app.config[PARSER_RESOURCE_KEY].graph), mimetype='text/plain')


@app.route('/parser/clear')
def clear():
    """Clears the content of the current graph"""
    app.config[PARSER_RESOURCE_KEY].clear()
    return "cleared"


if __name__ == '__main__':
    app.run()

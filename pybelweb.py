import io
import os

import flask
from flask import Flask, request, redirect, flash
from werkzeug.utils import secure_filename

from src.pybel_tools import owlparser

ALLOWED_OWL_EXTENSIONS = {'owl'}
ALLOWED_BEL_EXTENSIONS = {'bel'}

app = Flask(__name__)

if not os.path.exists(os.path.expanduser('~/.pybel')):
    os.mkdir(os.path.expanduser('~/.pybel'))
    os.mkdir(os.path.expanduser('~/.pybel/owl'))
    os.mkdir(os.path.expanduser('~/.pybel/bel'))

app.config['OWL_FOLDER'] = os.path.expanduser('~/.pybel/owl')
app.config['BEL_DIR'] = os.path.expanduser('~/.pybel/bel')


def allowed_file(filename, allowed_extensions):
    return '.' in filename and filename.rsplit('.', 1)[1] in allowed_extensions


@app.route('/', methods=['GET'])
def no_place_like_home():
    return app.send_static_file('index.html')


# OWL CONVERSION UTILITIES

@app.route('/asbel/', methods=['GET'])
def get_as_bel_listing():
    files = os.listdir(app.config['OWL_FOLDER'])
    files = [file for file in files if allowed_file(file, ALLOWED_OWL_EXTENSIONS)]
    files = ['<a href="/asbel/{path}">{path}</a>'.format(path=path) for path in files]
    html = '<html><h1>OWL Files</h1><ul>' + "\n".join(files) + '</ul></html>'
    return html


@app.route('/asbel/<ns>', methods=['GET'])
def get_as_bel(ns):
    if not ns.endswith('.owl'):
        return "invalid file extension for: {}".format(ns)

    path = os.path.join(app.config['OWL_FOLDER'], ns)
    if not os.path.exists(path):
        return "non-existent file: {}".format(ns)

    with open(path) as f:
        out_stream = io.StringIO()
        owlparser.build(f, out_stream)
        return flask.Response(out_stream.getvalue(), mimetype='text/plain')


@app.route('/conv', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']

        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)

        if file and allowed_file(file.filename, ALLOWED_OWL_EXTENSIONS):
            in_stream = io.StringIO(file.stream.getvalue().decode('utf-8'))
            out_stream = io.StringIO()
            try:
                owlparser.build(in_stream, out_stream)
            except Exception as e:
                return '{}<br>{}'.format(file.filename, e)
            # out_name = '{}.belns'.format(file.filename.split('.')[0])
            # out_stream.seek(0)
            # return flask.send_file(out_stream, attachment_filename=out_name, as_attachment=True)
            return flask.Response(out_stream.getvalue(), mimetype='text/plain')

    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Convert OWL File to BEL Namespace</h1>
    <form action="conv" method=post enctype=multipart/form-data>
        <p><input type=file name=file></p>
        <p><input type=submit value="Convert"></p>
    </form>
    '''


# BEL VALIDATOR
try:
    import pybel

    app.config['GRAPH'] = pybel.BELGraph()


    @app.route('/bel/validate', methods=['GET', 'POST'])
    def valiate():
        if request.method == 'POST':
            # check if the post request has the file part
            if 'file' not in request.files:
                flash('No file part')
                return redirect(request.url)
            file = request.files['file']

            if file.filename == '':
                flash('No selected file')
                return redirect(request.url)

            if file and allowed_file(file.filename, ALLOWED_BEL_EXTENSIONS):
                filename = secure_filename(file.filename)
                fp = os.path.join(app.config['BEL_DIR'], filename)

                qname = '.'.join(filename.split('.')[:-1])

                file.save(fp)

                # Queue this job
                app.config['GRAPH'].parse_from_path(fp)
                app.config['GRAPH'].to_pickle(os.path.join(app.config['BEL_DIR'], '{}.gpickle'.format(qname)))

                return "job done"
        return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Parse BEL File</h1>
    <form action="/bel/validate" method=post enctype=multipart/form-data>
        <p><input type=file name=file></p>
        <p><input type=submit value="Parse"></p>
    </form>
    '''


    @app.route('/bel/list', methods=['GET'])
    def list_bel():
        files = os.listdir(app.config['BEL_DIR'])
        bel_files = {file for file in files if allowed_file(file, ALLOWED_BEL_EXTENSIONS)}

        file_names = list(sorted('.'.join(file.split('.')[:-1]) for file in bel_files))

        links = []

        for fname in file_names:
            bel_link = '<a href="/bel/get/{path}.bel">{path}.bel</a>'.format(path=fname)
            pickle_link = '' if '{}.gpickle'.format(
                fname) not in files else '<a href="/bel/get/{path}.gpickle">{path}.gpickle</a>'.format(path=fname)
            links.append('<div>{} {}</div>'.format(bel_link, pickle_link))

        html = '<html><h1>BEL Files</h1><ul>' + "\n".join(links) + '</ul></html>'
        return html


    @app.route('/bel/get/<ns>', methods=['GET'])
    def get_bel(ns):
        if not ns.endswith('.bel') and not ns.endswith('.gpickle'):
            return "invalid file extension for: {}".format(ns)

        path = os.path.join(app.config['BEL_DIR'], ns)
        if not os.path.exists(path):
            return "non-existent file: {}".format(ns)

        return flask.send_file(path, mimetype='text/plain', as_attachment=True)
except:
    print('unable to load pybel')

if __name__ == '__main__':
    app.run()

import io
import os

import flask
from flask import Flask, request, redirect, flash

from src.pybel_tools import owlparser

ALLOWED_EXTENSIONS = {'owl'}
OWL_FOLDER = os.environ['OWL_FOLDER']

app = Flask(__name__)
app.config['OWL_FOLDER'] = OWL_FOLDER


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


@app.route('/', methods=['GET'])
def no_place_like_home():
    return app.send_static_file('index.html')


@app.route('/asbel/<ns>', methods=['GET'])
def get_as_bel(ns):
    if not ns.endswith('.owl'):
        return "invalid file extension for: {}".format(ns)

    path = os.path.expanduser(os.path.join(app.config['OWL_FOLDER'], ns))
    if not os.path.exists(path):
        return "non-existent file: {}".format(ns)

    with open(path) as f:
        out_stream = io.StringIO()
        owlparser.build(f, '', '', '', '', '', output=out_stream)
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

        if file and allowed_file(file.filename):
            in_stream = io.StringIO(file.stream.getvalue().decode('utf-8'))
            out_stream = io.StringIO()
            owlparser.build(in_stream, '', '', '', '', '', output=out_stream)
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


if __name__ == '__main__':
    app.run()

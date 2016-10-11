import io
import os

from flask import Flask, request, redirect, flash, Response

from src.pybel_tools import owlparser

UPLOAD_FOLDER = os.path.expanduser('~/Desktop/flaskups/')
ALLOWED_EXTENSIONS = {'owl'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


@app.route('/', methods=['GET', 'POST'])
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
            return Response(out_stream.getvalue(), mimetype='text/plain')

    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Convert OWL File to BEL Namespace</h1>
    <form action="" method=post enctype=multipart/form-data>
        <p><input type=file name=file></p>
        <p><input type=submit value="Convert"></p>
    </form>
    '''


if __name__ == '__main__':
    app.run()

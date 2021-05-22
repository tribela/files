import os
import tempfile

import markdown
from flask import Flask, render_template, request, send_from_directory, url_for

app = Flask(__name__)


@app.before_first_request
def setup():
    tmpdir = tempfile.gettempdir()
    uploaddir = os.path.join(tmpdir, 'files_upload')
    try:
        os.mkdir(uploaddir)
    except FileExistsError:
        pass

    app.config['UPLOAD_DIR'] = uploaddir


def is_cli():
    ua = request.headers.get('User-Agent', '')

    cli_ua = {
        'curl',
        'HTTPie'
    }

    return any(
        ua.startswith(x + '/')
        for x in cli_ua
    )


@app.get('/')
def index():
    url = url_for(upload_file.__name__, fname='hello.txt', _external=True)

    with open('usage.md') as f:
        md = f.read().replace('__url__', url)

    if is_cli():
        return md

    usage = markdown.markdown(md)

    return render_template('index.html', usage=usage)


@app.post('/<fname>')
def upload_file(fname):
    if 'file' not in request.files:
        return "File is required", 400

    file = request.files['file']
    file.save(os.path.join(app.config['UPLOAD_DIR'], fname))

    return url_for(get_file.__name__, fname=fname, _external=True)


@app.get('/<fname>')
def get_file(fname):
    return send_from_directory(
        app.config['UPLOAD_DIR'], fname,
        attachment_filename=fname)


@app.delete('/<fname>')
def delete_file(fname):
    try:
        os.remove(os.path.join(app.config['UPLOAD_DIR'], fname))
    except FileNotFoundError:
        return '', 404

    return 'OK'

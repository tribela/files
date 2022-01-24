import io
import os
import tempfile

import consolemd
import magic
import markdown
from flask import Flask, Response
from flask import render_template, request, send_from_directory, url_for
from werkzeug.middleware.proxy_fix import ProxyFix

app = Flask(__name__)

app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1)

FORBIDDEN_FILES = {
    'robots.txt',
}

MIME_OVERRIDES = {
    '.apk': 'application/vnd.android.package-archive',
}


@app.route('/robots.txt')
def robots():
    return send_from_directory(os.path.dirname(__file__), 'robots.txt')


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
        strio = io.StringIO()
        renderer = consolemd.Renderer(style_name='solarized-dark')
        renderer.render(md, output=strio)
        return Response(strio.getvalue(), mimetype='text/markdown')

    usage = markdown.markdown(md, extensions=['fenced_code', 'codehilite'])

    return render_template('index.html', usage=usage)


@app.route('/<fname>', methods=['PUT', 'POST'])
def upload_file(fname):
    if 'file' not in request.files:
        return "File is required", 400

    if fname in FORBIDDEN_FILES:
        return '', 403

    file = request.files['file']
    file.save(os.path.join(app.config['UPLOAD_DIR'], fname))

    return url_for(get_file.__name__, fname=fname, _external=True), 201


@app.get('/.upload/<fname>')
def upload(fname):
    return render_template('upload.html', fname=fname)


@app.get('/<fname>')
def get_file(fname):
    fpath = os.path.join(app.config['UPLOAD_DIR'], fname)
    ext = os.path.splitext(fname)[1]
    try:
        if ext in MIME_OVERRIDES:
            mimetype = MIME_OVERRIDES[ext]
        else:
            mime = magic.Magic(mime=True, mime_encoding=True)
            mimetype = mime.from_file(fpath)

        return send_from_directory(
            app.config['UPLOAD_DIR'], fname,
            attachment_filename=fname,
            mimetype=mimetype)
    except FileNotFoundError:
        return '', 405


@app.delete('/<fname>')
def delete_file(fname):
    if fname in FORBIDDEN_FILES:
        return '', 403

    try:
        os.remove(os.path.join(app.config['UPLOAD_DIR'], fname))
    except FileNotFoundError:
        return '', 404

    return 'OK'

import flask
import logging
import video_index.models
import video_index.templates
import waitress

log = logging.getLogger(__name__)
app = flask.Flask(__name__)


@app.before_request
def before_request():
    log.debug(f'{flask.request.method} {flask.request.path}')
    for k, v in flask.request.values.lists():
        log.debug(f'{k}: {v}')
    flask.g.model = video_index.models.get_model()


@app.route('/')
def index():
    return video_index.templates.index()


def main():
    video_index.models.get_model().migrate()
    waitress.serve(app, ident=None)

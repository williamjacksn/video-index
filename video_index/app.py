import flask
import logging
import video_index.models

log = logging.getLogger(__name__)
app = flask.Flask(__name__)


@app.before_request
def before_request():
    log.debug(f'{flask.request.method} {flask.request.path}')
    for k, v in flask.request.values.lists():
        log.debug(f'{k}: {v}')
    flask.g.model = video_index.models.get_model()


def main():
    video_index.models.get_model().migrate()

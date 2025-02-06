import flask
import logging
import pathlib
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


@app.route('/favicon.svg')
def favicon():
    return flask.Response(video_index.templates.favicon(), mimetype='image/svg+xml')


@app.route('/locations')
def locations():
    locs = video_index.models.get_model().locations_list()
    return video_index.templates.locations(locs)


@app.route('/locations/add', methods=['POST'])
def locations_add():
    root_folder = flask.request.values.get('root-folder')
    if root_folder:
        root_path = pathlib.Path(root_folder).resolve()
        if root_path.is_dir():
            video_index.models.get_model().locations_add(str(root_path))
    return flask.redirect(flask.url_for('locations'))


def main():
    video_index.models.get_model().migrate()
    waitress.serve(app, ident=None)

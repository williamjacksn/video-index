import flask
import logging
import pathlib
import video_index.models as m
import video_index.tasks as ta
import video_index.templates as te
import waitress

log = logging.getLogger(__name__)
app = flask.Flask(__name__)


@app.before_request
def before_request():
    log.debug(f'{flask.request.method} {flask.request.path}')
    for k, v in flask.request.values.lists():
        log.debug(f'{k}: {v}')


@app.route('/')
def index():
    return te.index()


@app.route('/favicon.svg')
def favicon():
    return flask.Response(te.favicon(), mimetype='image/svg+xml')


@app.route('/locations')
def locations():
    locs = m.get_model().locations_list()
    return te.locations(locs)


@app.route('/locations/add', methods=['POST'])
def locations_add():
    root_folder = flask.request.values.get('root-folder')
    if root_folder:
        root_path = pathlib.Path(root_folder).resolve()
        if root_path.is_dir():
            m.get_model().locations_add(str(root_path))
    return flask.redirect(flask.url_for('locations'))


@app.route('/locations/scan', methods=['POST'])
def locations_scan():
    root_folder = pathlib.Path(flask.request.values.get('root-folder')).resolve()
    loc = m.get_model().locations_get(root_folder)
    if loc:
        ta.scheduler.add_job(ta.scan_location, args=[loc.root_folder])
    return '', 204


def main():
    m.get_model().migrate()
    ta.scheduler.start()
    waitress.serve(app, ident=None)

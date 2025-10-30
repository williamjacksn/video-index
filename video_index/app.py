import logging
import pathlib

import flask
import waitress

import video_index.models as m
import video_index.tasks as ta
import video_index.templates as te

log = logging.getLogger(__name__)
app = flask.Flask(__name__)


@app.before_request
def before_request() -> None:
    log.debug(f"{flask.request.method} {flask.request.path}")
    for k, v in flask.request.values.lists():
        log.debug(f"{k}: {v}")


@app.route("/")
def index() -> str:
    return te.index()


@app.route("/favicon.svg")
def favicon() -> flask.Response:
    return flask.Response(te.favicon(), mimetype="image/svg+xml")


@app.route("/files/cards", methods=["POST"])
def files_cards() -> str:
    after = flask.request.values.get("after", "")
    missing_notes_only = "missing-notes-only" in flask.request.values
    q = flask.request.values.get("q")
    files = m.get_model().files_list(after, missing_notes_only, q)
    return te.files_list(files)


@app.route("/files/editable-note/<file_id>")
def files_editable_note(file_id: str) -> str:
    f = m.get_model().files_get(file_id)
    return te.files_editable_note(f)


@app.route("/files/get/<file_id>")
def files_get(file_id: str) -> flask.Response:
    f = m.get_model().files_get(file_id)
    return flask.send_file(f.file_path)


@app.route("/files/update-notes", methods=["POST"])
def files_update_notes() -> str:
    file_id = flask.request.values.get("file-id")
    notes = flask.request.values.get("notes")
    model = m.get_model()
    model.files_update_notes(file_id, notes)
    f = model.files_get(file_id)
    return te.files_update_notes(f)


@app.route("/locations")
def locations() -> str:
    locs = m.get_model().locations_list()
    return te.locations(locs)


@app.route("/locations/add", methods=["POST"])
def locations_add() -> flask.Response:
    root_folder = flask.request.values.get("root-folder")
    if root_folder:
        root_path = pathlib.Path(root_folder).resolve()
        if root_path.is_dir():
            m.get_model().locations_add(str(root_path))
    return flask.redirect(flask.url_for("locations"))


@app.route("/locations/scan", methods=["POST"])
def locations_scan() -> flask.Response:
    root_folder = pathlib.Path(flask.request.values.get("root-folder")).resolve()
    loc = m.get_model().locations_get(root_folder)
    if loc:
        ta.scheduler.add_job(ta.scan_location, args=[loc.root_folder])
    return flask.Response("", 204)


@app.route("/suffixes")
def suffixes() -> str:
    suffix_counts = m.get_model().suffixes_count()
    return te.suffixes(suffix_counts)


@app.route("/suffixes/enable", methods=["POST"])
def suffixes_enable() -> flask.Response:
    trigger_name = flask.request.headers.get("hx-trigger-name")
    suffix = pathlib.Path(trigger_name).suffix
    m.get_model().suffixes_enable(suffix, trigger_name in flask.request.values)
    return flask.Response("", 204)


def main() -> None:
    m.get_model().migrate()
    ta.scheduler.start()
    waitress.serve(app, ident=None, threads=8)

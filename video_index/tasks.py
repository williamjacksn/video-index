import logging
import pathlib

import apscheduler.schedulers.background

import video_index.models as m

log = logging.getLogger(__name__)
scheduler = apscheduler.schedulers.background.BackgroundScheduler()


def scan_location(root_folder: pathlib.Path) -> None:
    log.info(f"Scanning location {root_folder}")
    model = m.get_model()
    model.locations_scan_start(root_folder)
    folders = [root_folder]
    while folders:
        folder = folders.pop()
        log.debug(f"Scanning {folder}")
        for item in folder.iterdir():
            if item.is_dir():
                folders.append(item)
            else:
                model.files_add(item)
    model.locations_scan_complete(root_folder)
    log.info(f"Done scanning location {root_folder}")

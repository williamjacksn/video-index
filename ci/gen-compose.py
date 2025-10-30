import pathlib

import gen

this_file = pathlib.PurePosixPath(
    pathlib.Path(__file__).relative_to(pathlib.Path.cwd())
)

target = "compose.yaml"

content = {
    "services": {
        "app": {
            "image": "ghcr.io/williamjacksn/video-index",
            "init": True,
            "ports": ["8080:8080"],
            "volumes": ["./:/app"],
        },
        "shell": {
            "entrypoint": ["/bin/bash"],
            "image": "ghcr.io/williamjacksn/video-index",
            "init": True,
            "volumes": ["./:/app"],
        },
    },
    "configs": {
        "generator": {"content": f"This file ({target}) was generated from {this_file}"}
    },
}

gen.gen(content, target)

import gen

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
    }
}

gen.gen(content, "compose.yaml")

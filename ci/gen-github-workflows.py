import gen

build = {
    "name": "Build the container image",
    "on": {
        "pull_request": {"branches": ["main"]},
        "push": {"branches": ["main"]},
        "workflow_dispatch": {},
    },
    "permissions": {},
    "env": {
        "_workflow_file_generator": "ci/gen-github-workflows.py",
        "image_name": "ghcr.io/${{ github.repository }}",
    },
    "jobs": {
        "build": {
            "name": "Build the container image",
            "permissions": {"packages": "write"},
            "runs-on": "ubuntu-latest",
            "steps": [
                {
                    "name": "Set up Docker Buildx",
                    "uses": "docker/setup-buildx-action@v3",
                },
                {
                    "name": "Build the container image",
                    "uses": "docker/build-push-action@v6",
                    "with": {
                        "cache-from": "type=gha",
                        "cache-to": "type=gha,mode=max",
                        "tags": "${{ env.image_name }}:latest",
                    },
                },
                {
                    "name": "Log in to GitHub container registry",
                    "if": "github.event_name == 'push' || "
                    "github.event_name == 'workflow_dispatch'",
                    "uses": "docker/login-action@v3",
                    "with": {
                        "password": "${{ github.token }}",
                        "registry": "ghcr.io",
                        "username": "${{ github.actor }}",
                    },
                },
                {
                    "name": "Push latest image to registry",
                    "if": "github.event_name == 'push' || "
                    "github.event_name == 'workflow_dispatch'",
                    "uses": "docker/build-push-action@v6",
                    "with": {
                        "cache-from": "type=gha",
                        "push": True,
                        "tags": "${{ env.image_name }}:latest",
                    },
                },
            ],
        }
    },
}

gen.gen(build, ".github/workflows/build-container-image.yaml")

ruff = {
    "name": "Ruff",
    "on": {"pull_request": {"branches": ["main"]}, "push": {"branches": ["main"]}},
    "permissions": {"contents": "read"},
    "env": {
        "_workflow_file_generator": "ci/gen-github-workflows.py",
    },
    "jobs": {
        "ruff": {
            "name": "Run ruff linting and formatting checks",
            "runs-on": "ubuntu-latest",
            "steps": [
                {"name": "Check out repository", "uses": "actions/checkout@v5"},
                {
                    "name": "Run ruff check",
                    "uses": "astral-sh/ruff-action@v3",
                    "with": {"args": "check --output-format=github"},
                },
                {
                    "name": "Run ruff format",
                    "uses": "astral-sh/ruff-action@v3",
                    "with": {"args": "format --check"},
                },
            ],
        }
    },
}

gen.gen(ruff, ".github/workflows/ruff.yaml")

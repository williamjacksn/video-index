FROM ghcr.io/astral-sh/uv:0.8.22-trixie-slim

RUN /usr/sbin/useradd --create-home --shell /bin/bash --user-group python
USER python

WORKDIR /app
COPY --chown=python:python .python-version pyproject.toml uv.lock ./
RUN /usr/local/bin/uv sync --frozen

ENV PATH="/app/.venv/bin:${PATH}" \
    PYTHONDONTWRITEBYTECODE="1" \
    PYTHONUNBUFFERED="1" \
    TZ="Etc/UTC"

COPY --chown=python:python package.json run.py ./
COPY --chown=python:python video_index ./video_index

ENTRYPOINT ["/usr/local/bin/uv", "run", "run.py"]

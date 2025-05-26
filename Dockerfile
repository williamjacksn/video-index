FROM ghcr.io/astral-sh/uv:0.7.8 AS uv
FROM python:3.13-slim

COPY --from=uv /uv /bin/uv

RUN /usr/sbin/useradd --create-home --shell /bin/bash --user-group python
USER python

COPY --chown=python:python .python-version /home/python/video-index/.python-version
COPY --chown=python:python pyproject.toml /home/python/video-index/pyproject.toml
COPY --chown=python:python uv.lock /home/python/video-index/uv.lock
WORKDIR /home/python/video-index
RUN /bin/uv sync --frozen

ENV PYTHONDONTWRITEBYTECODE="1" \
    PYTHONUNBUFFERED="1" \
    TZ="Etc/UTC"

ENTRYPOINT ["/bin/uv", "run", "run.py"]

COPY --chown=python:python package.json /home/python/video-index/package.json
COPY --chown=python:python run.py /home/python/video-index/run.py
COPY --chown=python:python video_index /home/python/video-index/video_index

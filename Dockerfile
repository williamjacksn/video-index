FROM python:3.13-slim

RUN /usr/sbin/useradd --create-home --shell /bin/bash --user-group python

USER python
RUN /usr/local/bin/python -m venv /home/python/venv

COPY --chown=python:python requirements.txt /home/python/video-index/requirements.txt
RUN /home/python/venv/bin/pip install --no-cache-dir --requirement /home/python/video-index/requirements.txt

ENV HOME="/home/python" \
    PATH="/home/python/venv/bin:${PATH}" \
    PYTHONDONTWRITEBYTECODE="1" \
    PYTHONUNBUFFERED="1" \
    TZ="Etc/UTC"

WORKDIR /home/python/video-index
ENTRYPOINT ["/home/python/venv/bin/python", "/home/python/video-index/run.py"]

COPY --chown=python:python package.json /home/python/video-index/package.json
COPY --chown=python:python run.py /home/python/video-index/run.py
COPY --chown=python:python video_index /home/python/video-index/video_index

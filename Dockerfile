FROM python:3.9-alpine

ENV PYTHONFAULTHANDLER=1 \
  PYTHONUNBUFFERED=1 \
  PYTHONHASHSEED=random \
  PIP_NO_CACHE_DIR=off \
  PIP_DISABLE_PIP_VERSION_CHECK=on \
  PIP_DEFAULT_TIMEOUT=100

WORKDIR /app

RUN pip install pyinstaller

COPY . /app

RUN ls /app
RUN pyinstaller --onefile /app/dockiera-agent/src/agent/agent.py
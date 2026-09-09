# Python base for the pip-installable analysis tools. Each runner installs the
# package it needs into a venv at run time, so one image serves several tools
# and version pins stay visible in the runner rather than baked into a layer.
FROM python:3.11-slim
RUN apt-get update && apt-get install -y --no-install-recommends \
        git build-essential curl ca-certificates unzip file \
    && rm -rf /var/lib/apt/lists/*
RUN python3 -m venv /venv
ENV PATH="/venv/bin:${PATH}"
WORKDIR /work

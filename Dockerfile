# syntax = docker/dockerfile:1

FROM ubuntu:mantic as base

COPY --link . .

RUN apt-get update -qq && \
    apt-get install -y python-is-python3 python3.11-venv pkg-config build-essential python3-pip
RUN python3 -m venv .venv && \
    . .venv/bin/activate && \
    python3 -m pip install -r requirements.txt

CMD . .venv/bin/activate && python main.py

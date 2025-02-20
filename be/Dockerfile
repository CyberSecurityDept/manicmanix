FROM python:3.12-slim
LABEL maintainer="id.purwowd@gmail.com"

ENV PYTHONUNBUFFERED=1

COPY ./requirements.txt /requirements.txt
COPY ./modules_requirements.txt /modules_requirements.txt
COPY ./modules/ /modules

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    gcc libc-dev libjpeg-dev zlib1g-dev libffi-dev binutils android-tools-adb openssh-client usbutils \
    && pip install --upgrade pip \
    && pip install --no-cache-dir -r /requirements.txt \
    && pip install --no-cache-dir -r /modules_requirements.txt \
    && pip install -e modules/base/mvt \
    && apt-get remove -y gcc libc-dev \
    && apt-get autoremove -y \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir /app
WORKDIR /app
COPY . /app


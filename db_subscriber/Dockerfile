FROM python:3.9-slim

RUN addgroup user && adduser -h /home/user -D user -G user -s /bin/sh

COPY .  /usr/src/app/db-subscriber
WORKDIR  /usr/src/app/db-subscriber

RUN apt-get update \
    && apt-get install -y gcc libc-dev libxslt-dev libxml2 libpq-dev \
    && pip install --upgrade pip \
    && pip install -r ./db_subscriber/requirements.txt

EXPOSE 8080
CMD ["/usr/local/bin/uwsgi", "--ini", "server.ini"]
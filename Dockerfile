FROM python:3.10-alpine

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

COPY ./requirements.txt /usr/src/app/
RUN pip3 install --no-cache-dir -r requirements.txt

COPY log /usr/src/app/log
COPY config /usr/src/app/config
COPY config/config.json /usr/src/app/config/config.json

COPY . /usr/src/app
EXPOSE 8080

ENTRYPOINT ["python3"]
CMD ["-m", "server", "config/config.json"]


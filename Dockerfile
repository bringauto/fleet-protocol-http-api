FROM python:3.10-alpine

WORKDIR /home/bringauto

COPY ./requirements.txt /home/bringauto
RUN pip3 install --no-cache-dir -r requirements.txt

RUN mkdir /home/bringauto/log
COPY config /home/bringauto/config
COPY server /home/bringauto/server

EXPOSE 8080

ENTRYPOINT ["python3"]
CMD ["-m", "server", "config/config.json"]


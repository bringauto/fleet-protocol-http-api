FROM bringauto/python-environment:latest

WORKDIR /home/bringauto

COPY ./requirements.txt /home/bringauto
RUN "$PYTHON_ENVIRONMENT_PYTHON3" -m pip install --no-cache-dir -r requirements.txt

COPY config /home/bringauto/config
COPY server /home/bringauto/server

EXPOSE 8080

USER 5000:5000
RUN mkdir /home/bringauto/log

ENTRYPOINT ["bash", "-c", "$PYTHON_ENVIRONMENT_PYTHON3 -m server $0 $@"]
CMD ["config/config.json"]


ARG BUILD_FROM
FROM $BUILD_FROM

RUN \
  apk add --no-cache \
    python3 \
    py3-pip 

COPY requirements.txt /requirements.txt

COPY run.sh /
COPY app.py /app.py
RUN chmod a+x /run.sh

CMD [ "/run.sh" ]
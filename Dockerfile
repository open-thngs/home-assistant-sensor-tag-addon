ARG BUILD_FROM
FROM $BUILD_FROM

RUN \
  apk add --no-cache \
    python3 \
    py3-pip 

COPY requirements.txt /requirements.txt

COPY run.sh /
COPY src/udp.py /udp.py
RUN chmod a+x /run.sh

CMD [ "/run.sh" ]
FROM ftvsubtil/alpine-gpac

WORKDIR /app
ADD . .

RUN apk update && \
    apk add python3 && \
    pip3 install pika

CMD python3 src/worker.py
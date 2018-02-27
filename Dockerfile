FROM ftvsubtil/alpine-gpac

WORKDIR /app
ADD . .

RUN apk update && \
    apk add python3 && \
    pip3 install -r requirements.txt && \
    python3 setup.py install

CMD python3 gpac_worker/worker.py

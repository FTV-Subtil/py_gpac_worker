#!/usr/bin/env python

import configparser
import json
import traceback
import logging

from amqp_connection import Connection
import generate_dash
import ttml_to_mp4
import set_language

conn = Connection()

logging.basicConfig(
    format="%(asctime)-15s [%(levelname)s] %(message)s",
    level=logging.DEBUG,
)

config = configparser.RawConfigParser()
config.read([
    'worker.cfg',
    '/etc/py_gpac_worker/worker.cfg'
])

def callback(ch, method, properties, body):
    try:
        msg = json.loads(body.decode('utf-8'))
        logging.debug(msg)

        try:
            kind = msg['parameters']['kind']
            if kind == "generate_dash":
                generate_dash.process(conn, msg)
            elif kind == "ttml_to_mp4":
                ttml_to_mp4.process(conn, msg)
            elif kind == "set_language":
                set_language.process(conn, msg)
            else:
                error_content = {
                    "body": body.decode('utf-8'),
                    "error": "unable to process message, kind is not supported",
                    "job_id": msg['job_id'],
                    "type": "job_gpac"
                }
                conn.sendJson('job_gpac_error', error_content)

        except Exception as e:
            logging.error(e)
            traceback.print_exc()
            error_content = {
                "body": body.decode('utf-8'),
                "error": str(e),
                "job_id": msg['job_id'],
                "type": "job_gpac"
            }
            conn.sendJson('job_gpac_error', error_content)

    except Exception as e:
        logging.error(e)
        traceback.print_exc()
        error_content = {
            "body": body.decode('utf-8'),
            "error": str(e),
            "type": "job_gpac"
        }
        conn.sendJson('job_gpac_error', error_content)
    return True

conn.load_configuration(config['amqp'])

queues = [
    'job_gpac',
    'job_gpac_completed',
    'job_gpac_error'
]

conn.connect(queues)
conn.consume('job_gpac', callback)

#!/usr/bin/env python

import configparser
import json
import traceback
import logging
import os

from amqp_connection import Connection
import generate_dash
from parameters import get_parameter
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

def check_requirements(requirements):
    meet_requirements = True
    if 'paths' in requirements:
        required_paths = requirements['paths']
        assert isinstance(required_paths, list)
        for path in required_paths:
            if not os.path.exists(path):
                logging.debug("Warning: Required file does not exists: %s", path)
                meet_requirements = False

    return meet_requirements

def callback(ch, method, properties, body):
    try:
        msg = json.loads(body.decode('utf-8'))
        logging.debug(msg)

        try:
            parameters = msg['parameters']
            if 'requirements' in parameters:
                if not check_requirements(get_parameter(parameters, 'requirements')):
                    return False

            action = get_parameter(parameters, 'action')

            if action == "generate_dash":
                if generate_dash.process(conn, msg) == False:
                    return False
            elif action == "ttml_to_mp4":
                if ttml_to_mp4.process(conn, msg) == False:
                    return False
            elif action == "set_language":
                if set_language.process(conn, msg) == False:
                    return False
            else:
                error_content = {
                    "body": body.decode('utf-8'),
                    "error": "unable to process message, action is not supported",
                    "job_id": msg['job_id'],
                    "type": "job_gpac"
                }
                conn.publish_json('job_gpac_error', error_content)

        except Exception as e:
            logging.error(e)
            traceback.print_exc()
            error_content = {
                "body": body.decode('utf-8'),
                "error": str(e),
                "job_id": msg['job_id'],
                "type": "job_gpac"
            }
            conn.publish_json('job_gpac_error', error_content)

    except Exception as e:
        logging.error(e)
        traceback.print_exc()
        error_content = {
            "body": body.decode('utf-8'),
            "error": str(e),
            "type": "job_gpac"
        }
        conn.publish_json('job_gpac_error', error_content)
    return True


conn.run(
    config['amqp'],
    'job_gpac',
    [
        'job_gpac_completed',
        'job_gpac_error'
    ],
    callback
)

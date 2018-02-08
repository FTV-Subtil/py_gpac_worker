#!/usr/bin/env python

import os
import json
import traceback
import logging
import subprocess
import configparser

from amqp_connection import Connection

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

class GPAC_worker:

    def get_parameter(self, key, param):
        key = "GPAC_" + key
        if key in os.environ:
            return os.environ.get(key)

        return config.get('gpac', param)

    def load_configuration(self):
        self.gpac_bin_path = self.get_parameter('BIN_PATH', 'binpath')
        self.gpac_lib_path = self.get_parameter('LIB_PATH', 'libpath')
        self.mp4box_path = os.path.join(self.gpac_bin_path, "MP4Box")
        self.env = os.environ.copy()
        self.env["LD_LIBRARY_PATH"] = self.gpac_lib_path

    def process(self, src_path, dst_path, options: dict):

        command = [self.mp4box_path]
        for key, value in options.items():
            command.append(key)
            command.append(str(value))
        command.append("-out")
        command.append(dst_path)
        command.append(src_path)

        logging.debug("Launching process command: %s", ' '.join(command))
        gpac_process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env=self.env)
        output, errors = gpac_process.communicate()
        self.log_subprocess(output, errors)

        if errors:
            message = "An error occurred processing "
            message += src_path + ": "
            message += errors.decode("utf-8")
            raise RuntimeError(message)
        if gpac_process.returncode != 0:
            message = "Process returned with error "
            message += "(code: " + str(gpac_process.returncode) + "):\n"
            message += output.decode("utf-8")
            raise RuntimeError(message)

    def log_subprocess(self, stdout, stderr):
        if stdout:
            for line in stdout.decode("utf-8").split("\n"):
                logging.info("[GPAC Worker] " + line)
        if stderr:
            for line in stderr.decode("utf-8").split("\n"):
                logging.error("[GPAC Worker] " + line)


def callback(ch, method, properties, body):
    try:
        msg = json.loads(body.decode('utf-8'))
        logging.debug(msg)

        try:
            source = msg['parameters']['source']
            destination = msg['parameters']['destination']
            src_path = source['path']
            dst_path = destination['path']
            options = msg['parameters']['options']

            if not os.path.exists(os.path.dirname(dst_path)):
                os.makedirs(os.path.dirname(dst_path))

            worker = GPAC_worker()
            worker.load_configuration()
            worker.process(src_path, dst_path, options)

            logging.info("""End of process from %s to %s""",
                src_path,
                dst_path)

            body_message = {
                "status": "completed",
                "job_id": msg['job_id'],
            }

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

conn.load_configuration()

queues = [
    'job_gpac',
    'job_gpac_completed',
    'job_gpac_error'
]

conn.connect(queues)
conn.consume('job_gpac', callback)

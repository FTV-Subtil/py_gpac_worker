
import logging
import os

from gpac_worker import GPAC_worker
from parameters import get_parameter

def process(conn, msg):
    parameters = msg['parameters']
    src_path = get_parameter(parameters, 'source_path')
    dst_path = get_parameter(parameters, 'destination_path')

    if not os.path.exists(src_path):
        logging.error("Source path '%s' is not reachable or does not exists.", src_path)
        return False

    worker = GPAC_worker()
    worker.load_configuration()
    dst_path = worker.generate_mp4(src_path, dst_path)

    logging.info("""End of process from %s to %s""",
        src_path,
        dst_path)

    body_message = {
        "status": "completed",
        "job_id": msg['job_id'],
        "output": dst_path
    }

    conn.publish_json('job_gpac_completed', body_message)

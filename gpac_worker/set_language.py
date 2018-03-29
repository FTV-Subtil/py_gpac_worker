
import logging
import os
from gpac_worker import GPAC_worker

def process(conn, msg):
    src_path = msg['parameters']['source']['path']

    if not os.path.exists(src_path):
        logging.error("Source path '%s' is not reachable or does not exists.", src_path)
        return False

    options = msg['parameters']['options']
    if "-lang" not in options:
        raise RuntimeError("No language specified")

    worker = GPAC_worker()
    worker.load_configuration()
    dst_path = worker.set_language(src_path, options)

    logging.info("""End of process from %s to %s""",
        src_path,
        dst_path)

    body_message = {
        "status": "completed",
        "job_id": msg['job_id'],
        "output": dst_path
    }

    conn.publish_json('job_gpac_completed', body_message)


import logging

from gpac_worker import GPAC_worker
from parameters import get_parameter

def process(conn, msg):
    parameters = msg['parameters']
    src_paths = get_parameter(parameters, 'source_paths')
    dst_path = get_parameter(parameters, 'destination_path')

    if len(src_paths) == 0:
        raise RuntimeError("No source specified")

    worker = GPAC_worker()
    worker.load_configuration()
    dst_paths = worker.process(src_paths, dst_path, parameters)

    logging.info("""End of process from %s to %s""",
        src_paths,
        dst_paths)

    body_message = {
        "status": "completed",
        "job_id": msg['job_id'],
        "output": dst_paths
    }

    conn.publish_json('job_gpac_completed', body_message)

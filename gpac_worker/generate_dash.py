
import logging
from gpac_worker import GPAC_worker

def process(conn, msg):
    src_paths = msg['parameters']['source']['paths']
    if len(src_paths) == 0:
        raise RuntimeError("No source specified")
    # for path in src_paths:
    #     if not os.path.exists(path):
    #         logging.error("Source path '%s' is not reachable or does not exists.", path)
    #         return False

    options = msg['parameters']['options']

    worker = GPAC_worker()
    worker.load_configuration()
    dst_paths = worker.process(src_paths, options)

    logging.info("""End of process from %s to %s""",
        src_paths,
        dst_paths)

    body_message = {
        "status": "completed",
        "job_id": msg['job_id'],
        "output": dst_paths
    }

    conn.sendJson('job_gpac_completed', body_message)

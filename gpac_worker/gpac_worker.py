
import configparser
import logging
import os
import subprocess
import uuid

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
        self.gpac_bin_path = self.get_parameter('BIN_PATH', 'bin_path')
        self.gpac_lib_path = self.get_parameter('LIB_PATH', 'lib_path')
        self.gpac_output_dir_path = self.get_parameter('OUTPUT_PATH', 'output_path')
        self.mp4box_path = os.path.join(self.gpac_bin_path, "MP4Box")
        self.env = os.environ.copy()
        self.env["LD_LIBRARY_PATH"] = self.gpac_lib_path

    def process(self, src_paths: list, options: dict):

        if not options:
            options = dict()

        command = [self.mp4box_path]

        dst_dir = os.path.join(self.gpac_output_dir_path, str(uuid.uuid4()))
        dst_path = os.path.join(dst_dir, os.path.splitext(os.path.basename(src_paths[0]))[0] + "_dash.mpd")

        if "-out" in options:
            dst_path = options["-out"]
            dst_dir = os.path.dirname(dst_path)
            logging.warn("A custom output directory has been set: %s", dst_dir)
        else:
            options["-out"] = dst_path

        for key, value in options.items():
            command.append(key)
            if(value != True):
                command.append(str(value))

        for path in src_paths:
            command.append(path)

        if not os.path.exists(dst_dir):
            logging.debug("Create output directory: %s", dst_dir)
            os.makedirs(dst_dir)

        self.process_command(command)
        return [os.path.join(dst_dir, file) for file in os.listdir(dst_dir)]

    def generate_mp4(self, src_path, dst_path):
        command = [self.mp4box_path]
        command.append("-add")
        command.append(src_path)
        command.append(dst_path)
        self.process_command(command)
        return dst_path

    def process_command(self, command):
        logging.debug("Launching process command: %s", ' '.join(command))
        gpac_process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env=self.env)
        stdout, stderr = gpac_process.communicate()
        self.log_subprocess(stdout, stderr)

        if stderr:
            message = "An error occurred processing "
            message += src_paths + ": "
            message += stderr.decode("utf-8")
            raise RuntimeError(message)
        if gpac_process.returncode != 0:
            message = "Process returned with error "
            message += "(code: " + str(gpac_process.returncode) + "):\n"
            message += stdout.decode("utf-8")
            raise RuntimeError(message)

    def log_subprocess(self, stdout, stderr):
        if stdout:
            for line in stdout.decode("utf-8").split("\n"):
                logging.info("[GPAC Worker] " + line)
        if stderr:
            for line in stderr.decode("utf-8").split("\n"):
                logging.error("[GPAC Worker] " + line)

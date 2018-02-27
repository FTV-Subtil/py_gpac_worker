#!/usr/bin/env python

import os
from distutils.core import setup

dir_name = os.path.dirname(__file__)

setup(
    name = 'gpac_worker',
    version = '1.0',
    description = 'Python GPAC worker',
    license='MIT',
    keywords = [
        'GPAC',
        'DASH'
    ],
    author = 'Marc-Antoine ARNAUD, Valentin NOEL',
    author_email = 'arnaud.marcantoine@gmail.com',
    url = 'https://github.com/FTV-Subtil/py_gpac_worker',
    packages = [
        'gpac_worker'
    ],
    package_dir = {
        'gpac_worker': os.path.join(dir_name, 'gpac_worker')
    },
)

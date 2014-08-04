#!/usr/bin/env python

import pprint
import json
import os
import time

from kano.utils import run_cmd, download_url
from kano.logging import logger
from kano_world.connection import request_wrapper, content_type_json

def run(args):
    app_id = args[0]
    return app_id

def launch(app_id):
    cmd = "kano-apps"
    args = ["install", app_id]

    try:
        os.execvp(cmd, [cmd] + args)
    except:
        logger.error("Unable to launch kano-apps")

#!/usr/bin/env python

import pprint
import json
import os
import time

from kano.utils import run_cmd, download_url, is_running
from kano.gtk3.kano_dialog import KanoDialog
from kano.logging import logger
from kano_world.connection import request_wrapper, content_type_json

def run(args):
    app_id = args[0]

    if is_running("kano-apps"):
        dialog = KanoDialog(
            "Apps is already running",
            "You need to close it, before you can install an application.",
            {
                "OK": { "return_value": 0} ,
            },
        )
        dialog.run()
        raise Exception("kano-apps is already running.")

    return app_id

def launch(app_id):
    cmd = "kano-apps"
    args = ["install", app_id]

    try:
        os.execvp(cmd, [cmd] + args)
    except:
        logger.error("Unable to launch kano-apps")

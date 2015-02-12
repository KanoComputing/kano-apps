#!/usr/bin/env python

# apps.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#

import os

from kano.utils import is_running, pkill
from kano.gtk3.kano_dialog import KanoDialog
from kano.logging import logger


def run(args):
    app_id = args[0]

    kano_apps = "/usr/bin/python /usr/bin/kano-apps"
    if is_running(kano_apps):
        pkill(kano_apps)

    return app_id


def launch(app_id):
    cmd = "kano-apps"
    args = ["install", app_id]

    try:
        try:
            from kano_profile.tracker import track_data
            track_data("app-installed", app_id)
        except Exception:
            pass

        os.execvp(cmd, [cmd] + args)
    except:
        logger.error("Unable to launch kano-apps")

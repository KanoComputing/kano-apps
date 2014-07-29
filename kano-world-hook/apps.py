#!/usr/bin/env python

import pprint
import json
import os

from kano.utils import run_cmd, download_url
from kano.logging import logger
from kano_world.connection import request_wrapper, content_type_json
from kano_profile.apps import launch_project

def run(args):
    app_id = args[0]

    endpoint = '/apps/{}'.format(app_id)
    success, text, data = request_wrapper('get', endpoint, headers=content_type_json)
    if not success:
        raise Exception(text)

    data = data['app']

    # download the icon
    icon_file_type = data['icon_url'].split(".")[-1]
    icon_path = '/tmp/{}.{}'.format(app_id, icon_file_type)
    rv, err = download_url(data['icon_url'], icon_path)
    if not rv:
        raise Exception("Unable to download the icon file ({})".format(err))

    # Cleanup the JSON file
    data['icon'] = data['slug']
    del data['icon_url']
    del data['likes']
    del data['comments_count']

    # write out the data
    data_path = '/tmp/{}.app'.format(app_id)
    with open(data_path, 'w') as f:
        f.write(json.dumps(data))

    return [data_path, icon_path]

def launch(paths):
    data_path, icon_path = paths

    run_cmd("pkill chromium kano-world-launcher")

    cmd = "kano-apps"
    args = ["install", data_path, icon_path]

    try:
        os.execvp(cmd, [cmd] + args)
    except:
        logger.error("Unable to launch kano-apps")

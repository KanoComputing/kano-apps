# AppManage.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# Download, install and remove apps

import os
import json
import time

from kano_updater.utils import get_dpkg_dict
from kano.utils import run_cmd, download_url
from kano_world.connection import request_wrapper, content_type_json


def install_app(app, sudo_pwd=None, gui=True):
    pkgs = " ".join(app["packages"] + app["dependencies"])

    cmd = ""
    if gui:
        cmd = "rxvt -title 'Installing {}' -e bash -c ".format(app["title"])

    if sudo_pwd:
        cleanup_cmd = "echo {} | sudo -S dpkg --configure -a".format(sudo_pwd)
        update_cmd = "echo {} | sudo -S apt-get update".format(sudo_pwd)
        run = "echo {} | sudo -S apt-get install -y {}".format(sudo_pwd, pkgs)
    else:
        cleanup_cmd = "sudo dpkg --configure -a".format(sudo_pwd)
        update_cmd = "sudo apt-get update".format(sudo_pwd)
        run = "sudo apt-get install -y {}".format(pkgs)

    if gui:
        run = "'{}'".format(run)
    cmd += run

    # make sure there are no broken packages on the system
    run_cmd(cleanup_cmd)

    run_cmd(update_cmd)
    os.system(cmd)

    done = True
    installed_packages = get_dpkg_dict()[0]
    for pkg in app["packages"] + app["dependencies"]:
        if pkg not in installed_packages:
            done = False
            break

    return done


def uninstall_app(app, sudo_pwd=None):
    if len(app["packages"]) == 0:
        return True

    pkgs = " ".join(app["packages"])

    cmd = "rxvt -title 'Uninstalling {}' -e bash -c ".format(app["title"])
    if sudo_pwd:
        cmd += "'echo {} | sudo -S apt-get purge -y {}'".format(sudo_pwd, pkgs)
    else:
        cmd += "'sudo apt-get purge -y {}'".format(pkgs, sudo_pwd)
    os.system(cmd)

    done = True
    installed_packages = get_dpkg_dict()[0]
    for pkg in app["packages"]:
        if pkg in installed_packages:
            done = False
            break

    return done


def download_app(app_id_or_slug):
    endpoint = '/apps/{}'.format(app_id_or_slug)
    success, text, data = request_wrapper('get', endpoint, headers=content_type_json)
    if not success:
        endpoint = '/apps/slug/{}'.format(app_id_or_slug)
        success, text, data = request_wrapper('get', endpoint, headers=content_type_json)
        if not success:
            raise Exception(text)

    data = data['app']

    # download the icon
    icon_file_type = data['icon_url'].split(".")[-1]
    icon_path = '/tmp/{}.{}'.format(app_id_or_slug, icon_file_type)
    rv, err = download_url(data['icon_url'], icon_path)
    if not rv:
        raise Exception("Unable to download the icon file ({})".format(err))

    # Cleanup the JSON file
    data['icon'] = data['slug']
    del data['icon_url']
    del data['likes']
    del data['comments_count']
    data['time_installed'] = int(time.time())
    data['categories'] = map(lambda c: c.lower(), data['categories'])

    # write out the data
    data_path = '/tmp/{}.app'.format(app_id_or_slug)
    with open(data_path, 'w') as f:
        f.write(json.dumps(data))

    return [data_path, icon_path]

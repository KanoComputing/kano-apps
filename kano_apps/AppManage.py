# AppManage.py
#
# Copyright (C) 2014-2016 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# Download, install and remove apps


import os
import json
import time
import requests

from kano_apps.utils import get_dpkg_dict
from kano.utils import run_cmd, download_url, has_min_performance
from kano_world.connection import request_wrapper, content_type_json

KDESK_DIR = '~/.kdesktop/'
KDESK_EXEC = '/usr/bin/kdesk'


def run_sudo_cmd(cmd, pw=None):
    if pw:
        return run_cmd("echo {} | sudo -S {}".format(pw, cmd))
    else:
        return run_cmd("sudo -S {}".format(cmd))


def install_app(app, sudo_pwd=None, gui=True):
    pkgs = " ".join(app["packages"] + app["dependencies"])

    cmd = ""
    if gui:
        cmd = "rxvt -title 'Installing {}' -e bash -c ".format(app["title"])
        if sudo_pwd:
            cmd = "echo {} | sudo -S ".format(sudo_pwd) + cmd

    if sudo_pwd:
        cleanup_cmd = "echo {} | sudo -S dpkg --configure -a".format(sudo_pwd)
        update_cmd = "echo {} | sudo -S apt-get update".format(sudo_pwd)
        run = "sudo apt-get install -y {}".format(pkgs)
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
    os.system(cmd.encode('utf8'))

    done = True
    installed_packages = get_dpkg_dict()[0]
    for pkg in app["packages"] + app["dependencies"]:
        if pkg not in installed_packages:
            done = False
            break

    return done


def uninstall_packages(app, sudo_pwd=None):
    if len(app["packages"]) == 0:
        return True

    pkgs = " ".join(app["packages"])

    cmd = ("rxvt -title " + _("'Uninstalling {}'") + " -e bash -c ").format(app["title"])
    if sudo_pwd:
        cmd += "'echo {} | sudo -S apt-get purge -y {}'".format(sudo_pwd, pkgs)
    else:
        cmd += "'sudo apt-get purge -y {}'".format(pkgs, sudo_pwd)
    os.system(cmd.encode('utf8'))

    done = True
    installed_packages = get_dpkg_dict()[0]
    for pkg in app["packages"]:
        if pkg in installed_packages:
            done = False
            break

    return done


class AppDownloadError(Exception):
    pass


def query_for_app(app_id_or_slug):
    endpoint = '/api/apps/{}'.format(app_id_or_slug)
    url = 'https://apps-directory.os.kano.me{}'.format(endpoint)
    headers = { 'Content-Type': 'application/json' }

    print 'REQUEST 1', url
    r = requests.get(url, headers=headers)
    if not r.ok:
        endpoint = '/api/apps/slug/{}'.format(app_id_or_slug)
        url = 'https://apps-directory.os.kano.me{}'.format(endpoint)
        headers = { 'Content-Type': 'application/json' }

        print 'REQUEST 2', url
        r = requests.get(url, headers=headers)
        if not r.ok:
            raise AppDownloadError(r.content)

    return r.response.data['app']


def download_app(app_id_or_slug):
    data = query_for_app(app_id_or_slug)

    # download the icon
    icon_file_type = data['icon_url'].split(".")[-1]
    icon_path = '/tmp/{}.{}'.format(app_id_or_slug, icon_file_type)
    rv, err = download_url(data['icon_url'], icon_path)
    if not rv:
        msg = _("Unable to download the application ({})").format(err)
        raise AppDownloadError(msg)

    # Check if the app is going to run well on the hardware
    if 'min_performance_score' in data and \
       has_min_performance(data['min_performance_score']):

        msg = _(
            "{} won't be downloaded "
            "because the hardware is not performant enough"
        ).format(data['title'])
        raise AppDownloadError(msg)

    # Cleanup the JSON file
    data['icon'] = data['slug']
    del data['icon_url']
    del data['likes']
    del data['comments_count']
    data['time_installed'] = int(time.time())
    data['categories'] = map(lambda c: c.lower(), data['categories'])
    data['removable'] = True

    # FIXME: This should all be done in the API
    if 'priority' not in data:
        data['priority'] = get_prio(data['slug'])

    if data['slug'] == 'powerup':
        data['title'] = 'Make Light'

    # write out the data
    data_path = '/tmp/{}.app'.format(app_id_or_slug)
    with open(data_path, 'w') as f:
        f.write(json.dumps(data))

    return [data_path, icon_path]


def install_link_and_icon(app_name, app_data_file, app_icon_file, pw=None):
    app_icon_file_type = app_icon_file.split(".")[-1]

    # Install icon
    system_app_icon_file = "/usr/share/icons/Kano/66x66/apps/{}.{}".format(
        app_name, app_icon_file_type)
    run_sudo_cmd("mv {} {}".format(app_icon_file, system_app_icon_file),
                 pw)
    run_sudo_cmd("update-icon-caches {}".format("/usr/share/icons/Kano"),
                 pw)
    run_sudo_cmd("gtk-update-icon-cache-3.0", pw)

    # Install app file
    local_app_dir = "/usr/share/applications"
    run_sudo_cmd("mkdir -p {}".format(local_app_dir), pw)

    system_app_data_file = "{}/{}.app".format(local_app_dir, app_name)
    run_sudo_cmd("mv {} {}".format(app_data_file, system_app_data_file),
                 pw)
    run_sudo_cmd("update-app-dir", pw)

    return system_app_data_file


def uninstall_link_and_icon(app_name, pw=None):
    local_app_dir = "/usr/share/applications"
    system_app_data_file = "{}/{}.app".format(local_app_dir, app_name)
    run_sudo_cmd("rm -f {}".format(system_app_data_file), pw)
    run_sudo_cmd("update-app-dir", pw)

    system_app_icon_file = "/usr/share/icons/Kano/66x66/apps/{}.*".format(app_name)
    run_sudo_cmd("rm -f {}".format(system_app_icon_file), pw)
    run_sudo_cmd("update-icon-caches /usr/share/icons/Kano", pw)
    run_sudo_cmd("gtk-update-icon-cache-3.0", pw)


'''
Assigns priority to apps based on their name. Ideally this would be stored in
the API and we simply have to query it.

FIXME: Migrate this to the API
'''
def get_prio(slug):
    if slug == 'terminal-quest':
        return 725
    elif slug == 'powerup':
        return 525

    return 0

# AppManage.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# Download, install and remove apps

import os
import json
import time
import re

from gi.repository import Gtk, Gdk

from kano_updater.utils import get_dpkg_dict
from kano_apps.Media import media_dir
from kano.utils import run_cmd, download_url
from kano_world.connection import request_wrapper, content_type_json

KDESK_DIR = '~/.kdesktop/'
KDESK_EXEC = '/usr/bin/kdesk'

def install_app(app, sudo_pwd=None, gui=True, desktop=False):
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

    if done and desktop:
        add_to_desktop(app)

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
    success, text, data = request_wrapper(
        'get',
        endpoint,
        headers=content_type_json
    )

    if not success:
        endpoint = '/apps/slug/{}'.format(app_id_or_slug)
        success, text, data = request_wrapper(
            'get',
            endpoint,
            headers=content_type_json
        )

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


def _get_kdesk_icon_path(app):
    kdesk_dir = os.path.expanduser(KDESK_DIR)
    return kdesk_dir + re.sub(' ', '-', app["title"]) + ".lnk"


def _create_kdesk_icon(app):
    icon_theme = Gtk.IconTheme.get_default()
    icon_info = icon_theme.lookup_icon(app["icon"], 66, 0)

    icon = app["icon"]
    if icon_info is not None:
        icon = icon_info.get_filename()

    cmd = app["launch_command"]
    print cmd
    if type(app["launch_command"]) is dict:
        args = map(lambda s: "\"{}\"".format(s) if s.find(" ") >= 0 else s,
                   app["launch_command"]["args"])
        cmd = app["launch_command"]["cmd"]
        if len(args) > 0:
            cmd += " " + " ".join(args)

    kdesk_entry = 'table Icon\n'
    kdesk_entry += '  Caption:\n'
    kdesk_entry += '  AppID:\n'
    kdesk_entry += '  Command: {}\n'.format(cmd)
    kdesk_entry += '  Singleton: true\n'
    kdesk_entry += '  Icon: {}\n'.format(icon)
    kdesk_entry += '  IconHover: {}\n'.format(media_dir() +
                                              "icons/generic-hover.png")
    kdesk_entry += '  HoverXOffset: 0\n'
    kdesk_entry += '  Relative-To: grid\n'
    kdesk_entry += '  X: auto\n'
    kdesk_entry += '  Y: auto\n'
    kdesk_entry += 'end\n'

    kdesk_dir = os.path.expanduser(KDESK_DIR)
    if not os.path.exists(kdesk_dir):
        os.makedirs(kdesk_dir)

    icon_f = open(_get_kdesk_icon_path(app), 'w')
    icon_f.write(kdesk_entry)
    icon_f.close()


def add_to_desktop(app):
    display_name = Gdk.Display.get_default().get_name()
    kdesk_data_file = "/tmp/kdesk-metrics{}.dump".format(display_name)

    desktop_full = False
    if os.path.exists(kdesk_data_file):
        with open(kdesk_data_file, "r") as kdesk_data_f:
            kdesk_data = json.load(kdesk_data_f)
            if "grid_full" in kdesk_data:
                desktop_full = kdesk_data["grid-full"]

    if desktop_full is not True:
        _create_kdesk_icon(app)

        os.system('kdesk -i')
        return True

    return False


def remove_from_desktop(app):
    icon_loc = _get_kdesk_icon_path(app)
    if os.path.exists(icon_loc):
        os.unlink(icon_loc)

        os.system('kdesk -i')
        return True

    return False

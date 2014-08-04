# AppData.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# Which apps to look for on the system

import os
import re
import json
import time

from kano_updater.utils import get_dpkg_dict, install
from kano.utils import run_cmd, download_url
from kano.logging import logger
from kano_world.connection import request_wrapper, content_type_json


_SYSTEM_ICONS_LOC = '/usr/share/applications/'

def try_exec(app):
    path = None
    if len(app) <= 0:
        return False
    elif app[0] == '/':
        path = app
    else:
        for path in os.environ["PATH"].split(":"):
            possible_path = path + "/" + app
            if os.path.exists(possible_path):
                path = possible_path
                break

    return path != None and os.path.isfile(path) and os.access(path, os.X_OK)

def get_applications():
    loc = os.path.expanduser(_SYSTEM_ICONS_LOC)
    blacklist = [
        "idle3.desktop", "idle.desktop", "idle-python2.7.desktop",
        "idle-python3.2.desktop", "xarchiver.desktop", "make-minecraft.desktop",
        "make-music.desktop", "make-pong.desktop", "make-snake.desktop",
        "kano-video.desktop", "lxsession-edit.desktop", "lxrandr.desktop",
        "lxinput.desktop", "obconf.desktop", "openbox.desktop",
        "libfm-pref-apps.desktop", "lxappearance.desktop", "htop.desktop"
    ]
    apps = []
    if os.path.exists(loc):
        for f in os.listdir(_SYSTEM_ICONS_LOC):
            fp = os.path.join(loc, f)

            if os.path.isdir(fp):
                continue

            if f[-4:] == ".app":
                data = _load_from_app_file(fp)
                if data is not None:
                    apps.append(data)
                    if "overrides" in data:
                        blacklist += data["overrides"]

            if f[-8:] == ".desktop" and f[0:5] != "auto_":
                data = _load_from_dentry(fp)
                if data is not None:
                    apps.append(data)

    filtered_apps = []
    for app in apps:
        if os.path.basename(app["origin"]) in blacklist:
            continue

        filtered_apps.append(app)

    return sorted(filtered_apps, key=lambda a: a["title"])

def _load_from_app_file(app_path):
    with open(app_path, "r") as f:
        app = json.load(f)

    app["origin"] = app_path
    app["type"] = "app"
    app["launch_command"] = parse_command(app["launch_command"])

    return app

def _load_from_dentry(de_path):
    de = _parse_dentry(de_path)

    if "NoDisplay" in de and de["NoDisplay"] == "true":
        return

    app = {
        "type": "dentry",
        "origin": de_path,

        "title": de["Name"],
        "tagline": "",
        "launch_command": parse_command(de["Exec"]),

        "icon": de["Icon"],

        "packages": [],
        "dependencies": [],

        "removable": False,
    }

    if "Comment[en_GB]" in de:
        app["tagline"] = de["Comment[en_GB]"]
    elif "Comment" in de:
        app["tagline"] = de["Comment"]

    return app

def _parse_dentry(dentry_path):
    dentry_data = {}
    continuation = False
    cont_key = None
    with open(dentry_path, 'r') as dentry_file:
        for line in dentry_file.readlines():
            line = line.strip()
            if len(line) <= 0 or line == '[Desktop Entry]':
                continue

            if not continuation:
                split = line.split('=')

                key = split[0]
                value = '='.join(split[1:])
                dentry_data[key] = value
            else:
                dentry_data[cont_key] += "\n" + line

            if line[-1] == '\\':
                continuation = True
                cont_key = key
                dentry_data[key] = dentry_data[key][:-1]
            else:
                continuation = False
                cont_key = None

    return dentry_data

def install_app(app, sudo_pwd=None, gui=True):
    pkgs = " ".join(app["packages"] + app["dependencies"])

    cmd = ""
    if gui:
        cmd = "rxvt -title 'Installing {}' -e bash -c ".format(app["title"])

    if sudo_pwd:
        run = "echo {} | sudo -S apt-get install -y {}".format(sudo_pwd, pkgs)
        if gui:
            run = "'{}'".format(run)
        cmd += run
    else:
        run = "sudo apt-get install -y {}".format(pkgs)
        if gui:
            run = "'{}'".format(run)
        cmd += run

    rv = os.system(cmd)

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

    cmd =  "rxvt -title 'Uninstalling {}' -e bash -c ".format(app["title"])
    if sudo_pwd:
        cmd += "'echo {} | sudo -S apt-get remove -y {}'".format(sudo_pwd, pkgs)
    else:
        cmd += "'sudo apt-get remove -y {}'".format(pkgs, sudo_pwd)
    rv = os.system(cmd)

    done = True
    installed_packages = get_dpkg_dict()[0]
    for pkg in app["packages"]:
        if pkg in installed_packages:
            done = False
            break

    return done

def parse_command(cmd_line):
    cmd_line = re.sub(r'\%[fFuUpP]', '', cmd_line)

    split = cmd_line.split(' ')
    cmd = split[0]
    args = ' '.join(split[1:])

    token = ''
    tokens = []
    state = 'normal'
    for c in args:
        if state == 'normal':
            if c == '\'':
                state = 'single-quotes'
                if len(token) > 0:
                    tokens.append(token)
                token = ''
            elif c == '"':
                state = 'double-quotes'
                if len(token) > 0:
                    tokens.append(token)
                token = ''
            elif c == ' ':
                tokens.append(token)
                token = ''
            else:
                token += c
        elif state == 'single-quotes':
            if c == '\'':
                state = 'normal'
            else:
                token += c
        elif state == 'double-quotes':
            if c == '"':
                state = 'normal'
            else:
                token += c

    if len(token) > 0:
        tokens.append(token)

    return {'cmd': cmd, 'args': tokens}

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
    data['categories'] = map(data['categories'], lambda c: c.lower())

    # write out the data
    data_path = '/tmp/{}.app'.format(app_id_or_slug)
    with open(data_path, 'w') as f:
        f.write(json.dumps(data))

    return [data_path, icon_path]

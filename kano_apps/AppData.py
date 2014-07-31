# AppData.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# Which apps to look for on the system

import os
import re
import json
from kano_updater.utils import get_dpkg_dict, install

_SYSTEM_ICONS_LOC = '/usr/share/kano-applications/'
_INSTALLED_ICONS_LOC = '/usr/local/share/kano-applications/'
#_USER_ICONS_LOC = '~/.apps'
#_INSTALLERS_LOC = '/usr/share/kano-apps/installers'

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

def _load_apps_from_dir(loc):
    apps = []
    loc = os.path.expanduser(loc)
    if os.path.exists(loc):
        for app_file in os.listdir(loc):
            if app_file[-3:] != "app":
                continue

            app_file_path = loc + '/' + app_file
            if os.path.isdir(app_file_path):
                continue

            with open(app_file_path, "r") as f:
                apps.append(json.load(f))

    return apps

def get_applications():
    apps = _load_apps_from_dir(_SYSTEM_ICONS_LOC)
    apps += _load_apps_from_dir(_INSTALLED_ICONS_LOC)

    for app in apps:
        if 'launch_command' in app:
            app['launch_command'] = parse_command(app['launch_command'])

    return sorted(apps, key=lambda a: a['title'].lower())

def install_app(app, sudo_pwd=None):
    pkgs = " ".join(app["packages"] + app["dependencies"])

    cmd =  "rxvt -title 'Installing {}' -e bash -c ".format(app["title"])
    if sudo_pwd:
        cmd += "'echo {} | sudo -S apt-get install -y {}'".format(sudo_pwd, pkgs)
    else:
        cmd += "'sudo apt-get install -y {}'".format(pkgs, sudo_pwd)
    rv = os.system(cmd)

    done = True
    installed_packages = get_dpkg_dict()[0]
    for pkg in app["packages"] + app["dependencies"]:
        if pkg not in installed_packages:
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

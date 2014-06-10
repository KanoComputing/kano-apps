# AppData.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# Which apps to look for on the system

import os
import re

_KANO_ICONS_LOC = '/usr/share/kano-apps/extras'
_SYSTEM_ICONS_LOC = '/usr/share/kano-apps/apps'
_USER_ICONS_LOC = '~/.apps'
_INSTALLERS_LOC = '/usr/share/kano-apps/installers'

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

# types can be on of 'app', 'installer'
def _load_dentries_from_dir(loc, removable=False):
    dentries = []
    loc = os.path.expanduser(loc)
    if os.path.exists(loc):
        for dentry in os.listdir(loc):
            dentry_path = loc + '/' + dentry
            if os.path.isdir(dentry_path):
                continue

            dentry_data = _parse_dentry(dentry_path)
            if removable:
                dentry_data['icon_source'] = dentry_path
            dentries.append(dentry_data)

    return dentries

def get_applications():
    kano_icons = _load_dentries_from_dir(_KANO_ICONS_LOC)
    system_icons = _load_dentries_from_dir(_SYSTEM_ICONS_LOC)
    user_icons = _load_dentries_from_dir(_USER_ICONS_LOC, True)
    installers = _load_dentries_from_dir(_INSTALLERS_LOC)

    icons = []
    for app in kano_icons + system_icons + user_icons:
        if 'TryExec' in app:
            if not try_exec(app['TryExec']):
                continue
        icons.append(app)

    for installer in installers:
        if 'TryExec' in installer:
            if try_exec(installer['TryExec']):
                for icon in icons:
                    if 'TryExec' in icon and icon['TryExec'] == installer['TryExec']:
                        icon['Uninstall'] = installer['Exec']
            else:
                icons.append(installer)

    return sorted(icons, key=lambda d: d['Name'].lower())

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

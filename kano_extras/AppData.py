# kano-extras
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# Which apps to look for on the system

import os
import re

_SYSTEM_ICONS_LOC = '/usr/share/kano-extras/extras'
_USER_ICONS_LOC = '~/.extras'
_INSTALLERS_LOC = '/usr/share/kano-extras/installers'

def try_exec(app):
    path = None
    if len(app) <= 0:
        return false
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
def _load_dentries_from_dir(loc, dentry_type='app', removable=False):
    dentries = []
    loc = os.path.expanduser(loc)
    if os.path.exists(loc):
        for dentry in os.listdir(loc):
            dentry_path = loc + '/' + dentry
            if os.path.isdir(dentry_path):
                continue

            dentry_data = _parse_dentry(dentry_path)

            if dentry_type == 'installer':
                if 'TryExec' in dentry_data and not try_exec(dentry_data['TryExec']):
                    dentries.append(dentry_data)
            else:
                if 'TryExec' in dentry_data:
                    if try_exec(dentry_data['TryExec']):
                        dentries.append(dentry_data)
                else:
                    dentries.append(dentry_data)

            if removable:
                dentry_data['icon_source'] = dentry_path

    return dentries

def get_applications():

    system_icons = _load_dentries_from_dir(_SYSTEM_ICONS_LOC, 'app')
    user_icons = _load_dentries_from_dir(_USER_ICONS_LOC, 'app', True)
    installers = _load_dentries_from_dir(_INSTALLERS_LOC, 'installer')

    dentries = system_icons + user_icons + installers
    return sorted(dentries, key=lambda d: d['Name'].lower())

def parse_command(cmd_line):
    cmd_line = re.sub(r'\%[fFuU]', '', cmd_line)

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
    with open(dentry_path, 'r') as dentry_file:
        for line in dentry_file.readlines():
            line = line.strip()
            if len(line) <= 0 or line == '[Desktop Entry]':
                continue

            split = line.split('=')

            key = split[0]
            value = '='.join(split[1:])
            dentry_data[key] = value

    return dentry_data

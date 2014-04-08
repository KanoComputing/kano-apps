# kano-extras
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# Which apps to look for on the system

import os
import re

_DENTRY_LOCATIONS = ['/usr/share/kano-extras/extras', '~/.extras']
_INSTALLERS_LOCATIONS = ['/usr/share/kano-extras/installers']

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

def get_applications():
    dentries = []

    # process icons
    for loc in _DENTRY_LOCATIONS:
        if os.path.exists(loc):
            for dentry in os.listdir(os.path.expanduser(loc)):
                dentry_data = _parse_dentry(loc + '/' + dentry)
                if 'TryExec' in dentry_data:
                    if try_exec(dentry_data['TryExec']):
                        dentries.append(dentry_data)
                else:
                    dentries.append(dentry_data)

    # process installers
    for loc in _INSTALLERS_LOCATIONS:
        if os.path.exists(loc):
            for dentry in os.listdir(os.path.expanduser(loc)):
                dentry_data = _parse_dentry(loc + '/' + dentry)
                if 'TryExec' in dentry_data and not try_exec(dentry_data['TryExec']):
                    dentries.append(dentry_data)

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

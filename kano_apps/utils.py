# utils.py
#
# Copyright (C) 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#

from kano.utils import run_cmd


def get_dpkg_dict(include_unpacked=False):
    apps_ok = dict()
    apps_other = dict()

    cmd = 'dpkg -l'
    o, _, _ = run_cmd(cmd)
    lines = o.splitlines()
    for l in lines[5:]:
        parts = l.split()
        state = parts[0]
        name = parts[1]
        version = parts[2]

        if state == 'ii' or (include_unpacked and state == 'iU'):
            apps_ok[name] = version
        else:
            apps_other[name] = version

    return apps_ok, apps_other

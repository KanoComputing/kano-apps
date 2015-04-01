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

from kano_apps.Media import media_dir

KDESK_DIR = '~/.kdesktop/'
KDESK_EXEC = '/usr/bin/kdesk'

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
    kdesk_entry += '  X: 0\n'
    kdesk_entry += '  Y: 0\n'
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

        os.system('kdesk -r')
        return True

    return False


def remove_from_desktop(app):
    icon_loc = _get_kdesk_icon_path(app)
    if os.path.exists(icon_loc):
        os.unlink(icon_loc)

        os.system('kdesk -r')
        return True

    return False

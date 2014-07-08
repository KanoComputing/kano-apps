# Media.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# Functions related to artwork and media resources

import os
from gi.repository import Gtk, GdkPixbuf

MEDIA_LOCS = ['../media', '/usr/share/kano-apps/media']
APP_ICON_SIZE = 66


def media_dir():
    for path in MEDIA_LOCS:
        if os.path.exists(path):
            return os.path.abspath(path) + '/'

    raise Exception('Media directory not found.')


def get_app_icon(loc, size=APP_ICON_SIZE):
    try:
        pb = GdkPixbuf.Pixbuf.new_from_file_at_size(loc, size, size)
        icon = Gtk.Image.new_from_pixbuf(pb)
    except:
        icon = Gtk.Image.new_from_icon_name(loc, -1)
        icon.set_pixel_size(size)

    return icon

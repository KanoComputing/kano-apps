# UIElements.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# Different parts of the app's UI

from gi.repository import Gtk


class Contents(Gtk.EventBox):
    def __init__(self, win):
        Gtk.EventBox.__init__(self, hexpand=True, vexpand=True)

        style = self.get_style_context()
        style.add_class('contents')

        self._current = None
        self._win = win

    def get_window(self):
        return self._win

    def set_contents(self, obj):
        for w in self.get_children():
            self.remove(w)

        self.add(obj)
        obj.show_all()

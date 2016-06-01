# UIElements.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# Different parts of the app's UI

from gi.repository import Gtk

import pam
import getpass

from kano.gtk3.kano_dialog import KanoDialog


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

    def remove_contents(self):
        for w in self.get_children():
            self.remove(w)


def get_sudo_password(heading, parent=None):
    entry = Gtk.Entry()
    entry.set_visibility(False)
    kdialog = KanoDialog(
        title_text=heading,
        description_text=_("Enter your system password - default is kano:"),
        widget=entry,
        has_entry=True,
        global_style=True,
        parent_window=parent
    )

    pw = kdialog.run()
    del kdialog
    del entry

    while not pam.authenticate(getpass.getuser(), pw):
        fail = KanoDialog(
            title_text=heading,
            description_text=_("The password was incorrect. Try again?"),
            button_dict={
                _("YES"): {
                    "return_value": 0
                },
                _("CANCEL"): {
                    "return_value": -1,
                    "color": "red"
                }
            },
            parent_window=parent
        )

        rv = fail.run()
        del fail
        if rv < 0:
            return

        entry = Gtk.Entry()
        entry.set_visibility(False)
        kdialog = KanoDialog(
            title_text=heading,
            description_text=_("Re-enter your system password - default is kano:"),
            widget=entry,
            has_entry=True,
            global_style=True,
            parent_window=parent
        )

        pw = kdialog.run()
        del kdialog
        del entry

    return pw

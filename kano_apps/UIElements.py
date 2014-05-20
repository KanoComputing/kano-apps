# UIElements.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# Different parts of the app's UI

import os
import re
from gi.repository import Gtk, Gdk, Pango

from kano_apps.Media import media_dir, get_app_icon, get_ui_icon

class TopBar(Gtk.EventBox):
    _TOP_BAR_HEIGHT = 44

    def __init__(self):
        Gtk.EventBox.__init__(self)
        self.get_style_context().add_class('top_bar_container')

        box = Gtk.Box()
        box.set_size_request(-1, self._TOP_BAR_HEIGHT)

        self._header = Gtk.Label('Apps', halign=Gtk.Align.CENTER,
                                           valign=Gtk.Align.CENTER,
                                           hexpand=True)
        box.pack_start(self._header, True, True, 0)

        self._header.modify_font(Pango.FontDescription('Bariol 13'))
        self._header.get_style_context().add_class('header')

        # Close button
        cross_icon = get_ui_icon('cross')

        self._close_button = Gtk.Button()
        self._close_button.set_image(cross_icon)
        self._close_button.props.margin_right = 2
        self._close_button.set_can_focus(False)
        self._close_button.get_style_context().add_class('top_bar_button')
        self._close_button.get_style_context().add_class('no_border')

        self._close_button.connect('clicked', self._close_button_click)
        self._close_button.connect('enter-notify-event',
                                   self._close_button_mouse_enter)
        self._close_button.connect('leave-notify-event',
                                   self._close_button_mouse_leave)

        box.pack_start(self._close_button, False, False, 0)

        self.add(box)

    def _close_button_mouse_enter(self, button, event):
        # Change the cursor to hour Glass
        cursor = Gdk.Cursor.new(Gdk.CursorType.HAND1)
        self.get_root_window().set_cursor(cursor)

    def _close_button_mouse_leave(self, button, event):
        # Set the cursor to normal Arrow
        cursor = Gdk.Cursor.new(Gdk.CursorType.ARROW)
        self.get_root_window().set_cursor(cursor)

    def _close_button_click(self, event):
        cursor = Gdk.Cursor.new(Gdk.CursorType.ARROW)
        self.get_root_window().set_cursor(cursor)
        Gdk.flush()

        Gtk.main_quit()

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

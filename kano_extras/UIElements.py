# kano-extras
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# Different parts of the app's UI

import os
from gi.repository import Gtk, Gdk, Pango

from kano_extras import Media
from kano_extras.AppData import parse_command

class TopBar(Gtk.EventBox):
    _TOP_BAR_HEIGHT = 44

    def __init__(self):
        Gtk.EventBox.__init__(self)
        self.get_style_context().add_class('top_bar_container')

        box = Gtk.Box()
        box.set_size_request(-1, self._TOP_BAR_HEIGHT)

        self._header = Gtk.Label('Extras', halign=Gtk.Align.CENTER,
                                           valign=Gtk.Align.CENTER,
                                           hexpand=True)
        box.pack_start(self._header, True, True, 0)

        self._header.modify_font(Pango.FontDescription('Bariol 13'))
        self._header.get_style_context().add_class('header')

        # Close button
        cross_icon = Media.get_ui_icon('cross')

        self._close_button = Gtk.Button()
        self._close_button.set_image(cross_icon)
        self._close_button.props.margin_right = 2
        self._close_button.set_can_focus(False)
        self._close_button.get_style_context().add_class('top_bar_button')

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

class AppGridEntry(Gtk.EventBox):
    def __init__(self, label, desc, icon_loc, cmd):
        Gtk.EventBox.__init__(self)

        self._cmd = parse_command(cmd)

        entry = Gtk.Grid()
        entry.set_row_spacing(0)

        icon = Media.get_app_icon(icon_loc)
        icon.props.margin_left = 15
        icon.props.margin_right = 15
        icon.props.margin_top = 15
        icon.props.margin_bottom = 15
        entry.attach(icon, 0, 0, 1, 2)

        app_name = Gtk.Label(label, halign=Gtk.Align.START,
                                    valign=Gtk.Align.CENTER,
                                    hexpand=True)
        app_name.get_style_context().add_class('app_name')
        app_name.modify_font(Pango.FontDescription('Bariol bold 18'))
        app_name.props.margin_top = 25

        entry.attach(app_name, 1, 0, 1, 1)

        app_desc = Gtk.Label(desc,
                             halign=Gtk.Align.START,
                             valign=Gtk.Align.START,
                             hexpand=True)
        app_desc.get_style_context().add_class('app_desc')
        app_desc.modify_font(Pango.FontDescription('Bariol 12'))
        app_desc.props.margin_bottom = 25
        entry.attach(app_desc, 1, 1, 1, 1)

        self.add(entry)
        self.connect("enter-notify-event", self._mouse_enter)
        self.connect("leave-notify-event", self._mouse_leave)
        self.connect("button-release-event", self._mouse_click)

    def _mouse_enter(self, ebox, event):
        # Change the cursor to hour Glass
        cursor = Gdk.Cursor.new(Gdk.CursorType.HAND1)
        self.get_root_window().set_cursor(cursor)

    def _mouse_leave(self, ebox, event):
        # Set the cursor to normal Arrow
        cursor = Gdk.Cursor.new(Gdk.CursorType.ARROW)
        self.get_root_window().set_cursor(cursor)

    def _mouse_click(self, ebox, event):
        cursor = Gdk.Cursor.new(Gdk.CursorType.ARROW)
        self.get_root_window().set_cursor(cursor)
        Gdk.flush()

        os.execvp(self._cmd['cmd'], [self._cmd['cmd']] + self._cmd['args'])

class AppGrid(Gtk.ScrolledWindow):
    def __init__(self):
        Gtk.ScrolledWindow.__init__(self, hexpand=True, vexpand=True)
        self.props.margin_top = 20
        self.props.margin_bottom = 20
        self.props.margin_left = 20
        self.props.margin_right = 12

        self._number_of_entries = 0

        self._grid = Gtk.Grid()
        self._grid.props.margin_right = 10
        self.add_with_viewport(self._grid)

    def add_entry(self, app_name, label, desc, cmd):
        entry = AppGridEntry(app_name, label, desc, cmd)

        if (self._number_of_entries / 2) % 2:
            entry.get_style_context().add_class('appgrid_grey')

        xpos = self._number_of_entries % 2
        ypos = self._number_of_entries / 2
        self._grid.attach(entry, xpos, ypos, 1, 1)

        self._number_of_entries += 1

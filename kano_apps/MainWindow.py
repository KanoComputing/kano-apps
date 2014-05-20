# MainWindow.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# The MainWindow class

import os
from gi.repository import Gtk, Gdk

from kano_apps import Media
from kano_apps.UIElements import TopBar, Contents
from kano_apps.AppGrid import Apps
from kano_apps.AddDialog import AddDialog
from kano_apps.MoreView import MoreView
from kano_apps.AppData import get_applications

class MainWindow(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title='Kano Apps')

        self._last_page = 0

        # Set up window
        screen = Gdk.Screen.get_default()
        self._win_width = 850
        self._win_height = 595
        self.set_decorated(False)
        self.set_resizable(False)
        self.set_size_request(self._win_width, self._win_height)
        self.set_position(Gtk.WindowPosition.CENTER)

        # Destructor
        self.connect('delete-event', Gtk.main_quit)

        # Styling
        css_provider = Gtk.CssProvider()
        css_provider.load_from_path(Media.media_dir() + 'css/style.css')
        style_context = Gtk.StyleContext()
        style_context.add_provider_for_screen(screen, css_provider,
                                              Gtk.STYLE_PROVIDER_PRIORITY_USER)
        style = self.get_style_context()
        style.add_class('main_window')

        # Create elements
        self._grid = Gtk.Grid()
        self._top_bar = TopBar()
        self._grid.attach(self._top_bar, 0, 0, 1, 1)

        self._contents = Contents(self)
        self._grid.attach(self._contents, 0, 1, 1, 1)
        self._grid.set_row_spacing(0)
        self.add(self._grid)

        self.show_apps_view()

    def get_main_area(self):
        return self._contents

    def get_last_page(self):
        return self._last_page

    def set_last_page(self, last_page_num):
        self._last_page = last_page_num

    def show_apps_view(self):
        last_page = self.get_last_page()
        apps = Apps(get_applications(), self)
        self.get_main_area().set_contents(apps)
        apps.set_current_page(last_page)

    def show_more_view(self, app):
        more_view = MoreView(app, self)
        self.get_main_area().set_contents(more_view)

    def show_add_dialog(self):
        dialog = AddDialog(self._window)
        self.get_main_area().set_contents(dialog)

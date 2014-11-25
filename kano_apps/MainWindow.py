# MainWindow.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# The MainWindow class

import sys
import json

from gi.repository import Gtk, Gdk

from kano_apps import Media
from kano_apps.UIElements import Contents, get_sudo_password
from kano_apps.AppGrid import Apps
from kano_apps.AppData import get_applications
from kano_apps.AppManage import install_app, download_app, AppDownloadError, \
    install_link_and_icon
from kano_apps.AppInstaller import AppInstaller
from kano_apps.DesktopManage import add_to_desktop
from kano.gtk3.top_bar import TopBar
from kano.gtk3.application_window import ApplicationWindow
from kano.gtk3.kano_dialog import KanoDialog

try:
    from kano_profile.tracker import Tracker
    kanotracker = Tracker()
except:
    pass


class MainWindow(ApplicationWindow):
    def __init__(self, install=None, icon_only=False):
        ApplicationWindow.__init__(self, 'Apps', 755, 588)

        self._install = install
        self._icon_only = icon_only
        self._last_page = 0

        self.connect("show", self._app_loaded)

        # Destructor
        self.connect('delete-event', Gtk.main_quit)

        self.set_icon_from_file("/usr/share/kano-desktop/icons/apps.png")

        # Styling
        screen = Gdk.Screen.get_default()
        specific_css_provider = Gtk.CssProvider()
        specific_css_provider.load_from_path(Media.media_dir() +
                                             'css/style.css')
        specific_style_context = Gtk.StyleContext()
        specific_style_context.add_provider_for_screen(
            screen,
            specific_css_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_USER
        )
        style = self.get_style_context()
        style.add_class('main_window')

        # Create elements
        self._grid = Gtk.Grid()
        self._top_bar = TopBar("Apps", self._win_width, False)
        self._top_bar.set_close_callback(Gtk.main_quit)
        self._grid.attach(self._top_bar, 0, 0, 1, 1)

        self._contents = Contents(self)
        self._grid.attach(self._contents, 0, 1, 1, 1)
        self._grid.set_row_spacing(0)

        self.set_main_widget(self._grid)

        self.show_apps_view()

    def get_main_area(self):
        return self._contents

    def get_last_page(self):
        return self._last_page

    def set_last_page(self, last_page_num):
        self._last_page = last_page_num

    def show_apps_view(self, button=None, event=None):
        self._top_bar.disable_prev()
        self._apps = apps = Apps(get_applications(), self)
        self.get_main_area().set_contents(apps)

    def refresh(self, category=None):
        for app in get_applications():
            if self._apps.has_app(app):
                self._apps.update_app(app)
            else:
                self._apps.add_app(app)

    def _app_loaded(self, widget):
        if self._install is not None:
            self._install_apps()

    def _install_apps(self):
        pw = None
        for app in self._install:
            inst = AppInstaller(app, self._apps, pw, self)
            inst.set_check_if_installed(True)
            inst.set_icon_only(self._icon_only)
            inst.install()
            pw = inst.get_sudo_pw()

        self.set_last_page(0)
        self.refresh()

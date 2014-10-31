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
        apps.set_current_page(self.get_last_page())

    def refresh(self, category=None):
        last_page = self._apps.get_current_page()
        self.get_main_area().remove_contents()
        del self._apps

        self._apps = Apps(get_applications(), self)
        self.get_main_area().set_contents(self._apps)

        # FIXME: Momentarily disabling the tab switch
        # effectively fixes the bug where the scrollbars disappear,
        # but focus goes back to the first tab pane.
        #self._apps.set_current_page(last_page)

    def _app_loaded(self, widget):
        if self._install is not None:
            self._install_apps()

    def _install_apps(self):
        self.get_window().set_cursor(Gdk.Cursor(Gdk.CursorType.WATCH))
        for app in self._install:
            try:
                app_data_file, app_icon_file = download_app(app)
            except AppDownloadError as err:
                head = "Unable to download the application"
                dialog = KanoDialog(
                    head, str(err),
                    {
                        "OK": {
                            "return_value": 0
                        },
                    },
                    parent_window=self
                )
                dialog.run()
                del dialog
                sys.exit("{}: {}".format(head, str(err)))

            with open(app_data_file) as f:
                app_data = json.load(f)

            pw = get_sudo_password("Installing {}".format(app_data["title"]),
                                   self)
            if pw is None:
                return

            self.blur()

            while Gtk.events_pending():
                Gtk.main_iteration()

            success = True
            if not self._icon_only:
                success = install_app(app_data, pw)

            while Gtk.events_pending():
                Gtk.main_iteration()

            if success:
                # write out the tmp json
                with open(app_data_file, "w") as f:
                    f.write(json.dumps(app_data))

                install_link_and_icon(app_data['slug'], app_data_file,
                                      app_icon_file, pw)

                if not self._icon_only:
                    add_to_desktop(app_data)

                head = "Done!"
                message = app_data["title"] + " installed succesfully! " + \
                    "Look for it in the Apps launcher."
            else:
                head = "Installation failed"
                message = app_data["title"] + " cannot be installed at " + \
                    "the moment. Please make sure your kit is connected " + \
                    "to the internet and there is enough space left on " + \
                    "your card."

            dialog = KanoDialog(
                head,
                message,
                {
                    "OK": {
                        "return_value": 0
                    },
                },
            )
            dialog.run()
            del dialog

            self.unblur()

        self.set_last_page(0)
        self.refresh()
        self.get_window().set_cursor(Gdk.Cursor(Gdk.CursorType.ARROW))

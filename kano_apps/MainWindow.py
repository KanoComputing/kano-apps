# MainWindow.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# The MainWindow class

import sys
import json
import pam
import getpass

from gi.repository import Gtk, Gdk

from kano_apps import Media
from kano_apps.UIElements import Contents
from kano_apps.AppGrid import Apps
#from kano_apps.AddDialog import AddDialog
from kano_apps.MoreView import MoreView
from kano_apps.AppData import get_applications, install_app
from kano.gtk3.top_bar import TopBar
from kano.gtk3.apply_styles import apply_styles
from kano.gtk3.application_window import ApplicationWindow
from kano.gtk3.kano_dialog import KanoDialog
from kano.utils import run_cmd


class MainWindow(ApplicationWindow):
    def __init__(self):
        ApplicationWindow.__init__(self, 'Apps', 600, 488)

        self._last_page = 0

        self.connect("show", self._app_loaded)

        # Destructor
        self.connect('delete-event', Gtk.main_quit)

        self.set_icon_from_file("/usr/share/kano-desktop/icons/apps.png")

        # Styling
        screen = Gdk.Screen.get_default()
        specific_css_provider = Gtk.CssProvider()
        specific_css_provider.load_from_path(Media.media_dir() + 'css/style.css')
        specific_style_context = Gtk.StyleContext()
        specific_style_context.add_provider_for_screen(screen, specific_css_provider, Gtk.STYLE_PROVIDER_PRIORITY_USER)
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
        last_page = self.get_last_page()
        self._apps = apps = Apps(get_applications(), self)
        self.get_main_area().set_contents(apps)
        apps.set_current_page(last_page)

    def refresh(self, category=None):
        last_page = self._apps.get_current_page()
        self.get_main_area().remove_contents()
        del self._apps

        self._apps = Apps(get_applications(), self)
        self.get_main_area().set_contents(self._apps)

        if category:
            self._apps.set_current_page(self._apps.get_category_page(category))
        else:
            self._apps.set_current_page(last_page)

    def _app_loaded(self, widget):
        if len(sys.argv) >= 4 and sys.argv[1] == "install":
            app_data_file = sys.argv[2]
            app_icon_file = sys.argv[3]
            app_icon_file_type = app_icon_file.split(".")[-1]

            with open(app_data_file) as f:
                app_data = json.load(f)

            entry = Gtk.Entry()
            entry.set_visibility(False)
            kdialog = KanoDialog(
                title_text="Installing {}".format(app_data["title"]),
                description_text="Enter your sudo password:",
                widget=entry,
                has_entry=True,
                global_style=True,
                parent_window=self
            )

            pw = kdialog.run()
            del kdialog
            del entry

            while not pam.authenticate(getpass.getuser(), pw):
                fail = KanoDialog(
                    title_text="Installing {}".format(app_data["title"]),
                    description_text="The password was incorrect. Try again?",
                    button_dict={
                        "YES": {
                            "return_value": 0
                        },
                        "CANCEL INSTALLATION": {
                            "return_value": -1,
                            "color": "red"
                        }
                    },
                    parent_window=self
                )

                rv = fail.run()
                del fail
                if rv < 0:
                    return

                entry = Gtk.Entry()
                entry.set_visibility(False)
                kdialog = KanoDialog(
                    title_text="Installing {}".format(app_data["title"]),
                    description_text="Re-enter your sudo password:",
                    widget=entry,
                    has_entry=True,
                    global_style=True,
                    parent_window=self
                )

                pw = kdialog.run()
                del kdialog
                del entry

            self.blur()

            while Gtk.events_pending():
                Gtk.main_iteration()

            success = install_app(app_data, pw)

            head = "Installation failed"
            message = "{} cannot be installed at the moment.".format(app_data["title"]) + \
                      "Please make sure your kit is connected to the internet and there " + \
                      "is enough space left on your card."
            if success:
                # write out the tmp json
                with open(app_data_file, "w") as f:
                    f.write(json.dumps(app_data))

                local_app_dir = "/usr/local/share/kano-applications"
                run_cmd("echo {} | sudo mkdir -p {}".format(pw, local_app_dir))

                system_app_data_file = "{}/{}.app".format(local_app_dir, app_data["slug"])
                run_cmd("echo {} | sudo -S mv {} {}".format(pw, app_data_file, system_app_data_file))
                run_cmd("echo {} | sudo update-app-dir".format(pw))

                system_app_icon_file = "/usr/share/icons/Kano/66x66/apps/{}.{}".format(app_data["slug"], app_icon_file_type)
                run_cmd("echo {} | sudo mv {} {}".format(pw, app_icon_file, system_app_icon_file))
                run_cmd("echo {} | sudo update-icon-caches {}".format(pw, "/usr/share/icons/Kano"))

                head = "Done!"
                message = "{} installed succesfully!".format(app_data["title"])

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

            self.refresh()

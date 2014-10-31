# AppGrid.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#

import os
import re
import json
from gi.repository import Gtk, Gdk

from kano_apps.AppManage import install_app, uninstall_packages, KDESK_EXEC, \
    uninstall_link_and_icon, run_sudo_cmd
from kano_apps.DesktopManage import add_to_desktop, remove_from_desktop
from kano_apps.Media import media_dir, get_app_icon
from kano_apps.UIElements import get_sudo_password
from kano.gtk3.scrolled_window import ScrolledWindow
from kano.gtk3.cursor import attach_cursor_events
from kano.gtk3.kano_dialog import KanoDialog
from kano_updater.utils import get_dpkg_dict


class Apps(Gtk.Notebook):
    def __init__(self, apps, main_win):
        Gtk.Notebook.__init__(self)

        self._window = main_win
        self.connect("switch-page", self._switch_page)

        self._installed_packages = get_dpkg_dict()[0]

        want_more_app = {
            "type": "app",
            "title": "Want more apps?",
            "tagline": "Go to Kano World to install more",
            "slug": "want-more",

            "icon": "want-more-apps",
            "colour": "#fda96f",

            "categories": ["code", "media", "games", "others", "tools", "experimental"],

            "packages": [],
            "dependencies": ["chromium"],
            "launch_command": {"cmd": "kdesk-blur", "args": ["kano-world-launcher"]},
            "overrides": [],
            "desktop": False
        }
        apps.append(want_more_app)

        last_page = 0

        self._cat_names = ["latest", "code", "games", "media", "tools",
            "others", "experimental"]
        self._categories = {}

        for cat in self._cat_names:
            self._categories[cat] = AppGrid(main_win, self)
            label = Gtk.Label(cat.upper())
            self.append_page(self._categories[cat], label)

        for app in apps:
            self.add_app(app)

        self._window.set_last_page(last_page)

    def is_app_installed(self, app):
        for pkg in app["packages"] + app["dependencies"]:
            if pkg not in self._installed_packages:
                return False
        return True

    def _switch_page(self, notebook, page, page_num, data=None):
        self._window.set_last_page(page_num)

    def add_app(self, app):
        if not self.is_app_installed(app):
            app["_install"] = True

        self._apps[app["origin"]] = {"data": app, "entries": []}

        if app["type"] == "app":
            if "categories" in app:
                categories = map(lambda c: c.lower(), app["categories"])
                for cat in categories:
                    if cat in self._categories:
                        self._categories[cat].add_app(app)
        elif app["type"] == "dentry":
            self._categories["others"].add_app(app)

    def remove_app(self):
        pass

    def update_app(self):

class AppGrid(Gtk.EventBox):
    def __init__(self, main_win, app_objects):
        Gtk.EventBox.__init__(self, hexpand=True, vexpand=True)
        style = self.get_style_context()
        style.add_class('app-grid')

        self._win = main_win
        self._num_apps = 0

        self._sw = ScrolledWindow(hexpand=True, vexpand=True,
                                  wide_scrollbar=True)

        self._sw.props.margin_top = 7
        self._sw.props.margin_bottom = 0
        self._sw.props.margin_left = 0
        self._sw.props.margin_right = 0
        self._sw.props.border_width = 0
        self._sw.set_shadow_type(Gtk.ShadowType.NONE)

        self._box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        self._sw.add_with_viewport(self._box)
        self.add(self._sw)

    def add_app(self, app):
        if "colour" not in app:
            if (self._num_apps % 2) == 0:
                app["colour"] = "#f2914a"
            else:
                app["colour"] = "#f5a269"
            self._num_apps += 1

        entry = AppGridEntry(app, self._win)
        self._add_entry(entry)
        return entry

    def remove_app(self, app):
        pass

    def _add_entry(self, entry):
        entry.props.valign = Gtk.Align.START
        self._box.pack_start(entry, False, False, 0)

        entry_id = entry.get_app_id()
        if entry_id not in self._app_objects:
            self._app_objects[entry_id] = []

        self._app_objects[entry_id] = entry

    def get_num(self):
        return self._num_apps

class DesktopButton(Gtk.Button):
    _ADD_IMG_PATH = "{}/icons/desktop-add.png".format(media_dir())
    _RM_IMG_PATH = "{}/icons/desktop-rm.png".format(media_dir())

    def __init__(self, app):
        Gtk.Button.__init__(self, hexpand=False)

        self._app = app

        self.get_style_context().add_class('desktop-button')
        self.props.margin_right = 21
        self.connect("clicked", self._desktop_cb)
        self.refresh()
        self.show_all()

    def refresh(self):
        img = self.get_image()
        if img:
            img.destroy()

        if self._is_on_desktop():
            self.set_image(Gtk.Image.new_from_file(self._RM_IMG_PATH))
            self.set_tooltip_text("Remove from desktop")
        else:
            self.set_image(Gtk.Image.new_from_file(self._ADD_IMG_PATH))
            self.set_tooltip_text("Add to desktop")

    def _is_on_desktop(self):
        kdesk_dir = os.path.expanduser('~/.kdesktop/')
        file_name = re.sub(' ', '-', self._app["title"]) + ".lnk"
        return os.path.exists(kdesk_dir + file_name)

    def _desktop_cb(self, event):
        if not self._is_on_desktop():
            if add_to_desktop(self._app):
                self.refresh()
        else:
            if remove_from_desktop(self._app):
                self.refresh()

class AppGridEntry(Gtk.EventBox):
    def __init__(self, app, window):
        Gtk.EventBox.__init__(self)

        self._app = app
        self._cmd = app['launch_command']

        self.modify_bg(Gtk.StateType.NORMAL, Gdk.color_parse(app['colour']))

        self._window = window
        self._entry = entry = Gtk.HBox()

        self._icon = get_app_icon(app['icon'])
        self._icon.props.margin = 21

        entry.pack_start(self._icon, False, False, 0)

        texts = Gtk.VBox()

        name = app["title"]
        if "_install" in app:
            name = "Install {}".format(name)

        self._app_name = app_name = Gtk.Label(
            name,
            halign=Gtk.Align.START,
            valign=Gtk.Align.CENTER,
            hexpand=True
        )
        app_name.get_style_context().add_class('app_name')
        app_name.props.margin_top = 28

        texts.pack_start(app_name, False, False, 0)

        tagline = app['tagline']
        if tagline > 70:
            tagline = tagline[0:70]

        self._app_desc = app_desc = Gtk.Label(
            tagline,
            halign=Gtk.Align.START,
            valign=Gtk.Align.START,
            hexpand=True
        )
        app_desc.get_style_context().add_class('app_desc')
        app_desc.props.margin_bottom = 25

        texts.pack_start(app_desc, False, False, 0)
        entry.pack_start(texts, True, True, 0)

        if "description" in self._app:
            self._setup_desc_button()

        if "removable" in self._app and self._app["removable"] is True:
            self._setup_bin_button()

        self._setup_desktop_button()

        self.add(entry)
        attach_cursor_events(self)
        self.connect("button-release-event", self._entry_click_cb)

    def get_app_id(self):
        if "slug" in self._app:
            return self._app["slug"]
        else:
            return self._app["origin"]

    def _launch_app(self, cmd, args):
        try:
            os.execvp(cmd, [cmd] + args)
        except:
            pass

        # The execvp should not return, so if we reach this point,
        # there was an error.
        message = KanoDialog(
            "Error",
            "Unable to start the application.",
            {
                "OK": {
                    "return_value": 0,
                    "color": "red"
                }
            },
            parent_window=self._window
        )
        message.run()

    def _setup_desc_button(self):
        more_btn = Gtk.Button(hexpand=False)
        more = Gtk.Image.new_from_file("{}/icons/more.png".format(media_dir()))
        more_btn.set_image(more)
        more_btn.props.margin_right = 21
        more_btn.get_style_context().add_class('more-button')
        more_btn.connect("clicked", self._show_more_cb)
        more_btn.set_tooltip_text("More information")
        more_btn.connect("realize", self._set_cursor_to_hand_cb)
        self._entry.pack_start(more_btn, False, False, 0)

    def _setup_bin_button(self):
        remove_btn = Gtk.Button(hexpand=False)
        bin_open_img = "{}/icons/trashbin-open.png".format(media_dir())
        self._res_bin_open = Gtk.Image.new_from_file(bin_open_img)
        bin_closed_img = "{}/icons/trashbin-closed.png".format(media_dir())
        self._res_bin_closed = Gtk.Image.new_from_file(bin_closed_img)
        remove_btn.set_image(self._res_bin_closed)
        remove_btn.props.margin_right = 21
        remove_btn.get_style_context().add_class('more-button')
        remove_btn.connect("clicked", self._uninstall_cb)
        remove_btn.set_tooltip_text("Remove")
        remove_btn.connect("realize", self._set_cursor_to_hand_cb)
        remove_btn.connect("enter-notify-event", self._open_bin_cb)
        remove_btn.connect("leave-notify-event", self._close_bin_cb)
        self._entry.pack_start(remove_btn, False, False, 0)

    def _setup_desktop_button(self):
        self._desktop_btn = None
        print "PARTIAL YES"
        if "_install" not in self._app and \
           ("desktop" not in self._app or self._app["desktop"]):
            if os.path.exists(KDESK_EXEC):
                print "YES"
                self._desktop_btn = DesktopButton(self._app)
                self._entry.pack_start(self._desktop_btn, False, False, 0)

    def _set_cursor_to_hand_cb(self, widget, data=None):
        widget.get_window().set_cursor(Gdk.Cursor(Gdk.CursorType.HAND1))

    def _open_bin_cb(self, widget, event):
        widget.set_image(self._res_bin_open)

    def _close_bin_cb(self, widget, event):
        widget.set_image(self._res_bin_closed)

    def _show_more_cb(self, widget):
        kdialog = KanoDialog(
            self._app["title"],
            self._app['description'] if "description" in self._app else self._app['tagline'],
            {
                "OK, GOT IT": {
                    "return_value": 0,
                    "color": "green"
                }
            },
            parent_window=self._window
        )
        kdialog.set_action_background("grey")
        kdialog.title.description.set_max_width_chars(40)
        kdialog.run()

        return True

    def _entry_click_cb(self, ebox, event):
        if "_install" in self._app:
            self._install_cb()
        else:
            self._launch_app(self._cmd['cmd'], self._cmd['args'])

        return True

    def _uninstall_cb(self, event):
        confirmation = KanoDialog(
            title_text="Removing {}".format(self._app["title"]),
            description_text="This application will be uninstalled and " +
                             "removed from apps. Do you wish to proceed?",
            button_dict={
                "YES": {
                    "return_value": 0
                },
                "NO": {
                    "return_value": -1,
                    "color": "red"
                }
            },
            parent_window=self._window
        )
        confirmation.title.description.set_max_width_chars(40)

        rv = confirmation.run()
        del confirmation
        if rv < 0:
            return

        prompt = "Uninstalling {}".format(self._app["title"])
        pw = get_sudo_password(prompt, self._window)
        if pw is None:
            return

        while Gtk.events_pending():
            Gtk.main_iteration()

        success = uninstall_packages(self._app, pw)
        if success:
            remove_from_desktop(self._app)
            uninstall_link_and_icon(self._app["slug"])

        self.destroy()

    def _install_cb(self):
        pw = get_sudo_password("Installing {}".format(self._app["title"]),
                               self._window)
        if pw is None:
            return

        self._window.blur()
        self._window.get_window().set_cursor(Gdk.Cursor(Gdk.CursorType.WATCH))

        while Gtk.events_pending():
            Gtk.main_iteration()

        done = install_app(self._app, sudo_pwd=pw)

        self._window.get_window().set_cursor(Gdk.Cursor(Gdk.CursorType.ARROW))
        self._window.unblur()

        head = "Installation failed"
        message = self._app["title"] + " cannot be installed at the " + \
            "moment. Please make sure your kit is connected to the " + \
            "internet and there is enough space left on your card."
        if done:
            run_sudo_cmd("update-app-dir", pw)

            head = "Done!"
            message = "{} installed succesfully!".format(self._app["title"])

            del self._app["_install"]
            self._app_name.set_text(self._app["title"])
            add_to_desktop(self._app)
            self._setup_desktop_button()

        kdialog = KanoDialog(
            head, message,
            {
                "OK": {
                    "return_value": 0,
                    "color": "green"
                }
            },
            parent_window=self._window
        )
        kdialog.set_action_background("grey")
        kdialog.title.description.set_max_width_chars(40)

        kdialog.run()

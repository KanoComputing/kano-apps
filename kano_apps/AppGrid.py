# AppGrid.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#

import os
import re
import random
import json
from gi.repository import Gtk, Gdk

from kano_apps.AppData import parse_command, install_app, uninstall_app
from kano_apps.Media import media_dir, get_app_icon
from kano_apps.UIElements import get_sudo_password
from kano.gtk3.buttons import OrangeButton
from kano.gtk3.scrolled_window import ScrolledWindow
from kano.gtk3.cursor import attach_cursor_events
from kano.gtk3.kano_dialog import KanoDialog
from kano_updater.utils import get_dpkg_dict, install
from kano.utils import run_cmd

class Apps(Gtk.Notebook):
    def __init__(self, apps, main_win):
        Gtk.Notebook.__init__(self)

        self._window = main_win
        self.connect("switch-page", self._switch_page)

        self._installed_packages = get_dpkg_dict()[0]

        # split apps to 6 arrays
        latest_apps = []
        tools_apps = []
        others_apps = []
        games_apps = []
        code_apps = []
        media_apps = []

        for app in apps:
            if app["type"] == "app":
                if not self.is_app_installed(app):
                    app["_install"] = True

                if "time_installed" in app:
                    latest_apps.append(app)

                if "categories" in app:
                    categories = map(lambda c: c.lower(), app["categories"])
                    if "tools" in categories:
                        tools_apps.append(app)
                    if "others" in categories:
                        others_apps.append(app)
                    if "games" in categories:
                        games_apps.append(app)
                    if "code" in categories:
                        code_apps.append(app)
                    if "media" in categories:
                        media_apps.append(app)
                else:
                    others_apps.append(app)
            elif app["type"] == "dentry":
                others_apps.append(app)

        if len(latest_apps) > 0:
            latest_apps = sorted(latest_apps,
                lambda a1, a2: a1["time_installed"] > a2["time_installed"])
            latest = AppGrid(latest_apps[0:5], main_win)
            latest_label = Gtk.Label("LATEST")
            self.append_page(latest, latest_label)

        if len(games_apps) > 0:
            games = AppGrid(games_apps, main_win)
            games_label = Gtk.Label("GAMES")
            self.append_page(games, games_label)

        if len(media_apps) > 0:
            media = AppGrid(media_apps, main_win)
            media_label = Gtk.Label("MEDIA")
            self.append_page(media, media_label)

        if len(code_apps) > 0:
            code = AppGrid(code_apps, main_win)
            code_label = Gtk.Label("CODE")
            last_page = self.append_page(code, code_label)

        if len(tools_apps) > 0:
            tools = AppGrid(tools_apps, main_win)
            tools_label = Gtk.Label("TOOLS")
            self.append_page(tools, tools_label)

        if len(others_apps) > 0:
            others = AppGrid(others_apps, main_win)
            others_label = Gtk.Label("OTHERS")
            self.append_page(others, others_label)

            self._window.set_last_page(last_page)

    def is_app_installed(self, app):
        for pkg in app["packages"] + app["dependencies"]:
            if pkg not in self._installed_packages:
                return False
        return True

    def _switch_page(self, notebook, page, page_num, data=None):
        self._window.set_last_page(page_num)

class AppGrid(Gtk.EventBox):
    def __init__(self, apps, main_win):
        Gtk.EventBox.__init__(self, hexpand=True, vexpand=True)
        style = self.get_style_context()
        style.add_class('app-grid')

        self._sw = ScrolledWindow(hexpand=True, vexpand=True,
                                  wide_scrollbar=True)

        self._sw.props.margin_top = 7
        self._sw.props.margin_bottom = 0
        self._sw.props.margin_left = 0
        self._sw.props.margin_right = 0
        self._sw.props.border_width = 0
        self._sw.set_shadow_type(Gtk.ShadowType.NONE)

        self._box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        self._number_of_entries = 0
        self._entries = []

        i = 0
        for app in apps:
            if "colour" not in app:
                if (i % 2) == 0:
                    app["colour"] = "#f2914a"
                else:
                    app["colour"] = "#f5a269"
            i += 1
            self.add_entry(AppGridEntry(app, main_win))

        self._sw.add_with_viewport(self._box)
        self.add(self._sw)

    def add_entry(self, entry):
        entry.props.valign = Gtk.Align.START
        self._box.pack_start(entry, False, False, 0)


class AppGridEntry(Gtk.EventBox):
    _KDESK_DIR = '~/.kdesktop/'
    _KDESK_EXEC = '/usr/bin/kdesk'

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
        if tagline > 50:
            tagline = tagline[0:50]

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
            more_btn = Gtk.Button(hexpand=False)
            more = Gtk.Image.new_from_file("{}/icons/more.png".format(media_dir()))
            more_btn.set_image(more)
            more_btn.props.margin_right = 21
            #more_btn.props.valign = Gtk.Align.CENTER
            more_btn.get_style_context().add_class('more-button')
            more_btn.connect("clicked", self._show_more)
            more_btn.set_tooltip_text("More information")
            more_btn.connect("realize", self._set_cursor_to_hand)
            entry.pack_start(more_btn, False, False, 0)

        if "removable" in self._app and self._app["removable"] == True:
            remove_btn = Gtk.Button(hexpand=False)
            self._res_bin_open = Gtk.Image.new_from_file("{}/icons/trashbin-open.png".format(media_dir()))
            self._res_bin_closed = Gtk.Image.new_from_file("{}/icons/trashbin-closed.png".format(media_dir()))
            remove_btn.set_image(self._res_bin_closed)
            remove_btn.props.margin_right = 21
            #remove_btn.props.valign = Gtk.Align.CENTER
            remove_btn.get_style_context().add_class('more-button')
            remove_btn.connect("clicked", self._uninstall_app)
            remove_btn.set_tooltip_text("Remove")
            remove_btn.connect("realize", self._set_cursor_to_hand)
            remove_btn.connect("enter-notify-event", self._open_bin)
            remove_btn.connect("leave-notify-event", self._close_bin)
            entry.pack_start(remove_btn, False, False, 0)

        kdesk_dir = os.path.expanduser('~/.kdesktop/')
        file_name = re.sub(' ', '-', self._app["title"]) + ".lnk"
        on_desktop = os.path.exists(kdesk_dir + file_name)

        desktop_btn = Gtk.Button(hexpand=False)
        desktop_btn.props.margin_right = 21
        #desktop_btn.props.valign = Gtk.Align.CENTER

        if "_install" not in self._app:
            if os.path.exists(self._KDESK_EXEC):
                if on_desktop:
                    rm = Gtk.Image.new_from_file("{}/icons/desktop-rm.png".format(media_dir()))
                    desktop_btn.set_image(rm)
                    desktop_btn.get_style_context().add_class('desktop-button')
                    desktop_btn.connect("clicked", self._desktop_rm)
                    desktop_btn.set_tooltip_text("Remove from desktop")
                else:
                    add = Gtk.Image.new_from_file("{}/icons/desktop-add.png".format(media_dir()))
                    desktop_btn.set_image(add)
                    desktop_btn.get_style_context().add_class('desktop-button')
                    desktop_btn.connect("clicked", self._desktop_add)
                    desktop_btn.set_tooltip_text("Add to desktop")

            entry.pack_start(desktop_btn, False, False, 0)

        self.add(entry)
        attach_cursor_events(self)
        self.connect("button-release-event", self._mouse_click)

    def _set_cursor_to_hand(self, widget, data=None):
        widget.get_window().set_cursor(Gdk.Cursor(Gdk.CursorType.HAND1))

    def _open_bin(self, widget, event):
        widget.set_image(self._res_bin_open)

    def _close_bin(self, widget, event):
        widget.set_image(self._res_bin_closed)

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

    def _show_more(self, widget):
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
        response = kdialog.run()

        return True

    def _mouse_click(self, ebox, event):
        if "_install" in self._app:
            self._install()
        else:
            self._launch_app(self._cmd['cmd'], self._cmd['args'])

        return True

    def _uninstall_app(self, event):
        confirmation = KanoDialog(
            title_text="Removing {}".format(self._app["title"]),
            description_text="This application will be uninstalled and removed from apps. Do you wish to proceed?",
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

        rv = confirmation.run()
        del confirmation
        if rv < 0:
            return

        pw = get_sudo_password("Uninstalling {}".format(self._app["title"]), self._window)
        if pw is None:
            return

        while Gtk.events_pending():
            Gtk.main_iteration()

        success = uninstall_app(self._app, pw)
        if success:
            if os.path.exists(self._get_kdesk_icon_path()):
                self._desktop_rm()

            local_app_dir = "/usr/share/applications"
            system_app_data_file = "{}/{}.app".format(local_app_dir, self._app["slug"])
            run_cmd("echo {} | sudo -S rm -f {}".format(pw, system_app_data_file))
            run_cmd("echo {} | sudo -S update-app-dir".format(pw))

            system_app_icon_file = "/usr/share/icons/Kano/66x66/apps/{}.*".format(self._app["slug"])
            run_cmd("echo {} | sudo -S rm -f {}".format(pw, system_app_icon_file))
            run_cmd("echo {} | sudo -S update-icon-caches {}".format(pw, "/usr/share/icons/Kano"))

        self._window.refresh()

    def _install(self):
        done = install_app(self._app)

        head = "Installation failed"
        message = "{} cannot be installed at the moment.".format(self._app["title"]) + \
                  "Please make sure your kit is connected to the internet and there " + \
                  "is enough space left on your card."
        if done:
            head = "Done!"
            message = "{} installed succesfully!".format(self._app["title"])

            self._app_name.set_text(self._app["title"])
            del self._app["_install"]

        kdialog = KanoDialog(
            head, message,
            {
                "OK": {
                    "return_value": 0,
                    "color": "green"
                }
            },
            parent_window = self._window
        )
        kdialog.set_action_background("grey")

        response = kdialog.run()
        self._window.refresh()

    def _desktop_add(self, event):
        display_name = Gdk.Display.get_default().get_name()
        kdesk_data_file = "/tmp/kdesk-metrics{}.dump".format(display_name)

        desktop_full = False
        if os.path.exists(kdesk_data_file):
            with open(kdesk_data_file, "r") as f:
                kdesk_data = json.load(f)
                if "grid_full" in kdesk_data:
                    desktop_full = kdesk_data["grid-full"]

        if desktop_full != True:
            self._create_kdesk_icon()

            os.system('kdesk -r')
            self._window.refresh()

    def _desktop_rm(self, event=None):
        os.unlink(self._get_kdesk_icon_path())

        os.system('kdesk -r')
        self._window.refresh()

    def _get_kdesk_icon_path(self):
        kdesk_dir = os.path.expanduser(self._KDESK_DIR)
        return kdesk_dir + re.sub(' ', '-', self._app["title"]) + ".lnk"

    def _create_kdesk_icon(self):
        icon_theme = Gtk.IconTheme.get_default()
        icon_info = icon_theme.lookup_icon(self._app["icon"], 66, 0)

        icon = self._app["icon"]
        if icon_info != None:
            icon = icon_info.get_filename()

        args = map(lambda s: "\"{}\"".format(s) if s.find(" ") >= 0 else s, self._app["launch_command"]["args"])
        cmd = self._app["launch_command"]["cmd"]
        if len(args) > 0:
            cmd += " " + " ".join(args)

        kdesk_entry = 'table Icon\n'
        kdesk_entry += '  Caption:\n'
        kdesk_entry += '  AppID:\n'
        kdesk_entry += '  Command: {}\n'.format(cmd)
        kdesk_entry += '  Singleton: true\n'
        kdesk_entry += '  Icon: {}\n'.format(icon)
        kdesk_entry += '  IconHover: {}\n'.format(media_dir() + "icons/generic-hover.png")
        kdesk_entry += '  HoverXOffset: 0\n'
        kdesk_entry += '  Relative-To: grid\n'
        kdesk_entry += '  X: auto\n'
        kdesk_entry += '  Y: auto\n'
        kdesk_entry += 'end\n'

        kdesk_dir = os.path.expanduser(self._KDESK_DIR)
        if not os.path.exists(kdesk_dir):
            os.makedirs(kdesk_dir)

        f = open(self._get_kdesk_icon_path(), 'w')
        f.write(kdesk_entry)
        f.close()

#class AddButton(AppGridEntry):
#    def __init__(self, window):
#        self._window = window
#        app = {
#            'name': 'Add application',
#            'description': 'Want to access more apps?',
#            'icon': media_dir() + 'icons/add.png',
#            'exec': '',
#            'colour': '#F4A15D'
#        }
#        AppGridEntry.__init__(self, app, window)
#
#    def _mouse_click(self, ebox, event):
#        self._window.show_add_dialog()

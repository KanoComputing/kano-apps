# AppGrid.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#

import os
import re
import random
from gi.repository import Gtk, Gdk

from kano_apps.AppData import parse_command
from kano_apps.Media import media_dir, get_app_icon
from kano.gtk3.buttons import OrangeButton
from kano.gtk3.scrolled_window import ScrolledWindow
from kano.gtk3.cursor import attach_cursor_events
import kano.gtk3.kano_dialog as kano_dialog


class Apps(Gtk.Notebook):
    def __init__(self, apps, main_win):
        Gtk.Notebook.__init__(self)

        self._window = main_win
        self.connect("switch-page", self._switch_page)

        # split apps to 5 arrays
        tools_apps = []
        others_apps = []
        games_apps = []
        code_apps = []
        media_apps = []
        for app in apps:
            if "categories" in app:
                if "tools" in app["categories"]:
                    tools_apps.append(app)
                if "others" in app["categories"]:
                    others_apps.append(app)
                if "games" in app["categories"]:
                    games_apps.append(app)
                if "code" in app["categories"]:
                    code_apps.append(app)
                if "media" in app["categories"]:
                    media_apps.append(app)

        tools = AppGrid(tools_apps, main_win)
        others = AppGrid(others_apps, main_win)
        games = AppGrid(games_apps, main_win)
        code = AppGrid(code_apps, main_win)
        media = AppGrid(media_apps, main_win)

        games_label = Gtk.Label("GAMES")
        self.append_page(games, games_label)

        media_label = Gtk.Label("MEDIA")
        self.append_page(media, media_label)

        code_label = Gtk.Label("CODE")
        self.append_page(code, code_label)

        tools_label = Gtk.Label("TOOLS")
        self.append_page(tools, tools_label)

        others_label = Gtk.Label("OTHERS")
        self.append_page(others, others_label)

    def _switch_page(self, notebook, page, page_num, data=None):
        self._window.set_last_page(page_num)

class AppGrid(Gtk.EventBox):
    def __init__(self, apps, main_win):
        Gtk.EventBox.__init__(self, hexpand=True, vexpand=True)
        style = self.get_style_context()
        style.add_class('app-grid')

        self._sw = ScrolledWindow(hexpand=True, vexpand=True)

        self._sw.props.margin_top = 7
        self._sw.props.margin_bottom = 0
        self._sw.props.margin_left = 0
        self._sw.props.margin_right = 0
        self._sw.props.border_width = 0
        self._sw.set_shadow_type(Gtk.ShadowType.NONE)

        self._box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        self._number_of_entries = 0
        self._entries = []

        for app in apps:
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
        self._cmd = app['exec']

        self.modify_bg(Gtk.StateType.NORMAL, Gdk.color_parse(app['colour']))

        self._window = window
        self._entry = entry = Gtk.HBox()

        self._icon = get_app_icon(app['icon'])
        self._icon.props.margin = 21

        entry.pack_start(self._icon, False, False, 0)

        texts = Gtk.VBox()

        self._app_name = app_name = Gtk.Label(
            app['name'],
            halign=Gtk.Align.START,
            valign=Gtk.Align.CENTER,
            hexpand=True
        )
        app_name.get_style_context().add_class('app_name')
        app_name.props.margin_top = 28

        texts.pack_start(app_name, False, False, 0)

        self._app_desc = app_desc = Gtk.Label(
            app['description'],
            halign=Gtk.Align.START,
            valign=Gtk.Align.START,
            hexpand=True
        )
        app_desc.get_style_context().add_class('app_desc')
        app_desc.props.margin_bottom = 25

        texts.pack_start(app_desc, False, False, 0)

        entry.pack_start(texts, True, True, 0)

        if "help" in self._app:
            more_btn = Gtk.Button(vexpand=False, hexpand=False)
            more = Gtk.Image.new_from_file("{}/icons/more.png".format(media_dir()))
            more_btn.set_image(more)
            more_btn.props.margin_right = 21
            more_btn.props.valign = Gtk.Align.CENTER
            more_btn.get_style_context().add_class('more-button')
            more_btn.connect("clicked", self._show_more)
            more_btn.set_tooltip_text("More information")
            more_btn.connect("realize", self._set_cursor_to_hand)
            entry.pack_start(more_btn, False, False, 0)


        kdesk_dir = os.path.expanduser('~/.kdesktop/')
        file_name = re.sub(' ', '-', self._app["name"]) + ".lnk"
        on_desktop = os.path.exists(kdesk_dir + file_name)

        desktop_btn = Gtk.Button(vexpand=False, hexpand=False)
        desktop_btn.props.margin_right = 21
        desktop_btn.props.valign = Gtk.Align.CENTER

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

    def _launch_app(self, cmd, args):
        try:
            os.execvp(cmd, [cmd] + args)
        except:
            pass

        # The execvp should not return, so if we reach this point,
        # there was an error.
        message = Gtk.MessageDialog(type=Gtk.MessageType.ERROR,
                                    buttons=Gtk.ButtonsType.OK)
        message.set_markup("Unable to start the application.")
        message.run()
        message.destroy()

    def _show_more(self, widget):
        self._window.blur()
        kdialog = kano_dialog.KanoDialog(
            self._app["name"],
            self._app['help'] if "help" in self._app else self._app['description'],
            {
                "OK, GOT IT": {
                    "return_value": 0,
                    "color": "green"
                }
            }
        )
        kdialog.set_action_background("grey")
        response = kdialog.run()
        self._window.unblur()

        return True

    def _mouse_click(self, ebox, event):
        self._launch_app(self._cmd['cmd'], self._cmd['args'])
        return True

    def _desktop_add(self, event):
        self._create_kdesk_icon()

        os.system('kdesk -r')
        self._window.show_apps_view()

    def _desktop_rm(self, event):
        os.unlink(self._get_kdesk_icon_path())

        os.system('kdesk -r')
        self._window.show_apps_view()

    def _get_kdesk_icon_path(self):
        kdesk_dir = os.path.expanduser(self._KDESK_DIR)
        return kdesk_dir + re.sub(' ', '-', self._app["name"]) + ".lnk"

    def _create_kdesk_icon(self):
        kdesk_entry = 'table Icon\n'
        kdesk_entry += '  Caption:\n'
        kdesk_entry += '  AppID:\n'
        kdesk_entry += '  Command: {}\n'.format(self._app["exec"])
        kdesk_entry += '  Singleton: true\n'
        kdesk_entry += '  Icon: {}\n'.format(self._app["icon"])
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

class SystemApp:
    pass

class UserApp(SystemApp):
    def __init__(self, app, window):
        SystemApp.__init__(self, app, window)

        self._icon_source = app['icon_source']

        self._add_link("Remove", self._remove_mouse_click)

    def _remove_mouse_click(self, widget, event):
        os.unlink(self._icon_source)

        kdesk_dir = os.path.expanduser("~/.kdesktop")
        kdesk_icon = kdesk_dir + "/" + re.sub(' ', '-', self._app["name"]) + ".lnk"

        if os.path.exists(kdesk_icon):
            os.unlink(kdesk_icon)
            os.system("kdesk -r")

        self._window.show_apps_view()
        return True


class UninstallableApp(SystemApp):
    def __init__(self, app, window):
        SystemApp.__init__(self, app, window)

        # Deal with the params placeholder
        uninstall_cmd = re.sub(r'\%[pP]', 'uninstall', app['Uninstall'])
        self._uninstall_cmd = parse_command(uninstall_cmd)

        self._add_link("Uninstall", self._remove_mouse_click)

    def _remove_mouse_click(self, widget, event):
        self._launch_app(self._uninstall_cmd['cmd'], self._uninstall_cmd['args'])


class AddButton(AppGridEntry):
    def __init__(self, window):
        self._window = window
        app = {
            'name': 'Add application',
            'description': 'Want to access more apps?',
            'icon': media_dir() + 'icons/add.png',
            'exec': '',
            'colour': '#F4A15D'
        }
        AppGridEntry.__init__(self, app, window)

    def _mouse_click(self, ebox, event):
        self._window.show_add_dialog()

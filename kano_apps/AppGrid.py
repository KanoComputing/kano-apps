# AppGrid.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#

import os
import re
from gi.repository import Gtk

from kano_apps.AppData import parse_command
from kano_apps.Media import media_dir, get_app_icon
from kano.gtk3.buttons import OrangeButton
from kano.gtk3.scrolled_window import ScrolledWindow
from kano.gtk3.cursor import attach_cursor_events


class Apps(Gtk.Notebook):
    def __init__(self, apps, main_win):
        Gtk.Notebook.__init__(self)

        self._window = main_win
        self.connect("switch-page", self._switch_page)

        # split apps to 3 arrays
        tools_apps = []
        extras_apps = []
        user_apps = []
        for app in apps:
            if "Categories" in app:
                cats = app["Categories"].split(";")
                if "Tools" in cats:
                    tools_apps.append(app)
                if "Extras" in cats:
                    extras_apps.append(app)
                if "User" in cats:
                    user_apps.append(app)

        tools = AppGrid(tools_apps, main_win)
        extras = AppGrid(extras_apps, main_win)

        user = AppGrid(user_apps, main_win)
        user.add_entry(AddButton(main_win))

        tools_label = Gtk.Label("TOOLS")
        self.append_page(tools, tools_label)

        extras_label = Gtk.Label("EXTRAS")
        self.append_page(extras, extras_label)

        user_label = Gtk.Label("USER")
        self.append_page(user, user_label)

    def _switch_page(self, notebook, page, page_num, data=None):
        self._window.set_last_page(page_num)


class AppGrid(Gtk.EventBox):
    def __init__(self, apps, main_win):
        Gtk.EventBox.__init__(self, hexpand=True, vexpand=True)

        self._sw = ScrolledWindow(hexpand=True, vexpand=True)

        style = self.get_style_context()
        style.add_class('app-grid')

        self._sw.props.margin_top = 20
        self._sw.props.margin_bottom = 20
        self._sw.props.margin_left = 20
        self._sw.props.margin_right = 12

        self._grid = Gtk.Grid()
        self._number_of_entries = 0
        self._entries = []

        for app in apps:
            entry = None
            if 'Uninstall' in app:
                entry = UninstallableApp(app, main_win)
            elif 'icon_source' in app:
                entry = UserApp(app, main_win)
            else:
                entry = SystemApp(app, main_win)
            self.add_entry(entry)

        self._sw.add_with_viewport(self._grid)
        self.add(self._sw)

    def add_entry(self, entry):
        if (self._number_of_entries / 2) % 2:
            entry.get_style_context().add_class('appgrid_grey')

        xpos = self._number_of_entries % 2
        ypos = self._number_of_entries / 2
        self._grid.attach(entry, xpos, ypos, 1, 1)

        self._number_of_entries += 1
        self._entries.append(entry)


class AppGridEntry(Gtk.EventBox):
    def __init__(self, label, desc, icon_loc, window):
        Gtk.EventBox.__init__(self)

        self._window = window

        self._entry = entry = Gtk.Grid()
        entry.set_row_spacing(0)

        self._icon = icon = get_app_icon(icon_loc)
        icon.props.margin = 15
        entry.attach(icon, 0, 0, 1, 3)

        self._app_name = app_name = Gtk.Label(label, halign=Gtk.Align.START,
                                              valign=Gtk.Align.CENTER,
                                              hexpand=True)
        app_name.get_style_context().add_class('app_name')
        app_name.props.margin_top = 25

        entry.attach(app_name, 1, 0, 1, 1)

        self._app_desc = app_desc = Gtk.Label(desc,
                                              halign=Gtk.Align.START,
                                              valign=Gtk.Align.START,
                                              hexpand=True)
        app_desc.get_style_context().add_class('app_desc')
        app_desc.props.margin_bottom = 25
        entry.attach(app_desc, 1, 1, 1, 1)

        self._app_name.props.margin_top = 14
        self._app_desc.props.margin_bottom = 0

        self._links = Gtk.HBox(False, 0)
        self._links.props.margin_bottom = 14
        entry.attach(self._links, 1, 2, 1, 1)
        self._links_count = 0

        self.add(entry)
        attach_cursor_events(self)
        self.connect("button-release-event", self._mouse_click)

    def _add_link(self, label, callback):
        ebox = OrangeButton(label)

        if self._links_count:
            spacer = Gtk.Label("|", halign=Gtk.Align.START,
                               valign=Gtk.Align.START)
            spacer.get_style_context().add_class('app_link_spacer')
            self._links.pack_start(spacer, False, False, 2)

        self._links.pack_start(ebox, False, False, 2)

        self._links_count += 1

        ebox.connect("button-release-event", callback)

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

    def _mouse_click(self, ebox, event):
        pass


class SystemApp(AppGridEntry):
    def __init__(self, app, window):
        AppGridEntry.__init__(self, app['Name'], app['Comment[en_GB]'],
                              app['Icon'], window)

        self._app = app

        self._cmd = parse_command(app['Exec'])
        self._add_link("More", self._show_more)

    def _show_more(self, widget, event):
        self._window.show_more_view(self._app)
        return True

    def _mouse_click(self, ebox, event):
        self._launch_app(self._cmd['cmd'], self._cmd['args'])


class UserApp(SystemApp):
    def __init__(self, app, window):
        SystemApp.__init__(self, app, window)

        self._icon_source = app['icon_source']

        self._add_link("Remove", self._remove_mouse_click)

    def _remove_mouse_click(self, widget, event):
        os.unlink(self._icon_source)
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
        AppGridEntry.__init__(self, 'Add application',
                              'Want to access more apps?',
                              media_dir() + 'icons/add.png', window)

    def _mouse_click(self, ebox, event):
        self._window.show_add_dialog()

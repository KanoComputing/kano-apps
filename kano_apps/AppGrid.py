# AppGrid.py
#
# Copyright (C) 2014-2016 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#

import os
import re
from gi.repository import Gtk, Gdk

from kano_apps.AppManage import uninstall_packages, KDESK_EXEC, \
    uninstall_link_and_icon
from kano_apps.AppData import load_from_app_file
from kano_apps.DesktopManage import add_to_desktop, remove_from_desktop
from kano_apps.Media import media_dir, get_app_icon
from kano_apps.UIElements import get_sudo_password
from kano_apps.AppInstaller import AppInstaller
from kano.gtk3.scrolled_window import ScrolledWindow
from kano.gtk3.cursor import attach_cursor_events
from kano.gtk3.kano_dialog import KanoDialog


class Apps(Gtk.Notebook):
    def __init__(self, apps, main_win):
        Gtk.Notebook.__init__(self)

        self._window = main_win
        self.connect("switch-page", self._switch_page)

        want_more_app = {
            "type": "app",
            "title": _("Want more apps?"),
            "tagline": _("Go to Kano World to install more"),
            "slug": "want-more",

            "origin": "-",

            "icon": "want-more-apps",
            "colour": "#fda96f",

            "categories": ["code", "media", "games", "others",
                           "tools", "experimental"],

            "packages": [],
            "dependencies": ["chromium"],
            "launch_command": {"cmd": "kdesk-blur",
                               "args": ["kano-world-launcher /apps/"]},
            "overrides": [],
            "desktop": False
        }

        last_page = 0

        self._cat_names = ["latest", "code", "games", "media", "tools",
                           "others", "experimental"]
        self._categories = {}

        self._apps = {}

        # Determine which categories have apps (the others won't be shown)
        used_categories = set(["latest", "others"])
        for app in apps:
            if 'categories' in app:
                for category in app['categories']:
                    if category in self._cat_names:
                        used_categories.add(category)

        # Sort the categories to the predetermined order
        sorted_categories = sorted(used_categories, lambda a, b:
                                   cmp(self._cat_names.index(a),
                                       self._cat_names.index(b)))

        # Prepare tabs for the apps
        for cat in sorted_categories:
            self._categories[cat] = AppGrid(main_win, self)
            label = Gtk.Label(cat.upper())
            ebox = Gtk.EventBox()
            ebox.add(label)
            ebox.connect("realize", self._set_cursor_to_hand_cb)
            ebox.show_all()
            self.append_page(self._categories[cat], ebox)
            self._categories[cat].new_entry(want_more_app)

        for app in apps:
            self.add_app(app)

        self._window.set_last_page(last_page)

    def has_app(self, app):
        if "origin" in app:
            return app["origin"] in self._apps
        elif "slug" in app:
            for origin, app_obj in self._apps.iteritems():
                if "slug" in app_obj["data"] and \
                   app_obj["data"]["slug"] == app["slug"]:
                    return True

        return False

    def has_slug(self, slug):
        for origin, app_obj in self._apps.iteritems():
            if "slug" in app_obj["data"] and \
               app_obj["data"]["slug"] == slug:
                return True

        return False

    def _switch_page(self, notebook, page, page_num, data=None):
        self._window.set_last_page(page_num)

    def add_app(self, app_data):
        if app_data["origin"] in self._apps:
            return

        self._apps[app_data["origin"]] = {"data": app_data, "entries": []}
        app_entries = self._apps[app_data["origin"]]["entries"]

        if app_data["type"] == "app":
            if "categories" in app_data:
                categories = map(lambda c: c.lower(), app_data["categories"])
                shown = False
                for cat in categories:
                    if cat in self._categories:
                        cat_obj = self._categories[cat]
                        entry = cat_obj.new_entry(app_data)
                        app_entries.append(entry)
                        shown = True
                # If the app doesn't fall under any category, it will be put
                # inside others
                if not shown:
                    cat_obj = self._categories["others"]
                    entry = cat_obj.new_entry(app_data)
                    app_entries.append(entry)
        elif app_data["type"] == "dentry":
            entry = self._categories["others"].new_entry(app_data)
            app_entries.append(entry)

        if "time_installed" in app_data:
            entry = self._categories["latest"].new_entry(
                app_data, "time_installed", True)
            app_entries.append(entry)

    def remove_app(self, app_data):
        origin = app_data["origin"]

        for entry in self._apps[origin]["entries"]:
            entry.destroy()

        del self._apps[origin]

    def update_app(self, app_data):
        origin = app_data["origin"]
        self._apps[origin]["data"] = app_data
        for entry in self._apps[origin]["entries"]:
            entry.refresh(app_data)

    def _set_cursor_to_hand_cb(self, widget, data=None):
        widget.get_window().set_cursor(Gdk.Cursor(Gdk.CursorType.HAND1))


class AppGrid(Gtk.EventBox):
    def __init__(self, main_win, apps_obj):
        Gtk.EventBox.__init__(self, hexpand=True, vexpand=True)
        style = self.get_style_context()
        style.add_class('app-grid')

        self._win = main_win
        self._apps = apps_obj
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

    def new_entry(self, app, sort_by="title", reverse=False):
        if "colour" not in app:
            if (self._num_apps % 2) == 0:
                app["colour"] = "#f2914a"
            else:
                app["colour"] = "#f5a269"
            self._num_apps += 1

        entry = AppGridEntry(app, self._win, self._apps)
        self._box.pack_start(entry, False, False, 0)

        pos = 0
        for child in self._box:
            child_app_data = child.get_app_data()

            # keep the special "want-more" entry at the bottom of the list
            if "slug" in child_app_data and \
               child_app_data["slug"] == "want-more":
                break

            if reverse:
                if app[sort_by] > child_app_data[sort_by]:
                    break
            else:
                if app[sort_by] < child_app_data[sort_by]:
                    break

            pos += 1

        self._box.reorder_child(entry, pos)

        entry.show_all()
        return entry

    def get_num(self):
        return self._num_apps


class DesktopButton(Gtk.Button):
    _ADD_IMG_PATH = "{}/icons/desktop-add.png".format(media_dir())
    _RM_IMG_PATH = "{}/icons/desktop-rm.png".format(media_dir())

    def __init__(self, app, apps_obj):
        Gtk.Button.__init__(self, hexpand=False)

        self._app = app
        self._apps = apps_obj

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
            self.set_tooltip_text(_("Remove from desktop"))
        else:
            self.set_image(Gtk.Image.new_from_file(self._ADD_IMG_PATH))
            self.set_tooltip_text(_("Add to desktop"))

        self.show_all()

    def _is_on_desktop(self):
        kdesk_dir = os.path.expanduser('~/.kdesktop/')
        file_name = re.sub(' ', '-', self._app["title"]) + ".lnk"
        return os.path.exists(kdesk_dir + file_name)

    def _desktop_cb(self, event):
        if not self._is_on_desktop():
            if add_to_desktop(self._app):
                self._apps.update_app(self._app)
        else:
            if remove_from_desktop(self._app):
                self._apps.update_app(self._app)


class AppGridEntry(Gtk.EventBox):
    def __init__(self, app, window, apps_obj):
        Gtk.EventBox.__init__(self)

        self.props.valign = Gtk.Align.START

        self._apps = apps_obj

        self._app = app
        self._cmd = app['launch_command']

        self._window = window
        self._entry = entry = Gtk.HBox()

        self.modify_bg(Gtk.StateType.NORMAL, Gdk.color_parse(app['colour']))

        self._icon = get_app_icon(app['icon'])
        self._icon.props.margin = 21
        entry.pack_start(self._icon, False, False, 0)

        texts = Gtk.VBox()

        # Initialise the app title label
        self._app_name = app_name = Gtk.Label(
            "",
            halign=Gtk.Align.START,
            valign=Gtk.Align.CENTER,
            hexpand=True
        )
        app_name.get_style_context().add_class('app_name')
        app_name.props.margin_top = 28
        texts.pack_start(app_name, False, False, 0)
        self._set_title(app)

        # Initialise the app desc label
        self._app_desc = app_desc = Gtk.Label(
            "",
            halign=Gtk.Align.START,
            valign=Gtk.Align.START,
            hexpand=True
        )
        app_desc.get_style_context().add_class('app_desc')
        app_desc.props.margin_bottom = 25
        texts.pack_start(app_desc, False, False, 0)
        self._set_tagline(app)

        entry.pack_start(texts, True, True, 0)

        self._update_btn = None
        if "_update" in self._app and self._app["_update"] is True:
            self._setup_update_button()

        self._more_btn = None
        if "description" in self._app:
            self._setup_desc_button()

        self._remove_btn = None
        if "removable" in self._app and self._app["removable"] is True:
            self._setup_remove_button()

        self._setup_desktop_button()

        self.add(entry)
        attach_cursor_events(self)
        self.connect("button-press-event", self._entry_click_cb)

    def get_app_data(self):
        return self._app

    def refresh(self, new_app_data):
        old_app_data = self._app
        self._app = new_app_data

        if old_app_data["icon"] != new_app_data["icon"]:
            self._icon.set_from_pixbuf(get_app_icon(new_app_data['icon']).get_pixbuf())

        if "colour" in new_app_data and old_app_data["colour"] != new_app_data["colour"]:
            self.modify_bg(Gtk.StateType.NORMAL, Gdk.color_parse(new_app_data["colour"]))

        self._set_title(new_app_data)
        self._set_tagline(new_app_data)

        # Refresh update button
        if "_update" in old_app_data and "_update" not in new_app_data:
            # remove button
            self._update_btn.destroy()
            self._update_btn = None
        if "_update" not in old_app_data and "_update" in new_app_data:
            # add button
            self._setup_update_button()

        # Refresh description button
        if "description" in old_app_data and "description" not in new_app_data:
            # remove button
            self._more_btn.destroy()
            self._more_btn = None
        if "description" not in old_app_data and "description" in new_app_data:
            # add button
            self._setup_desc_button()

        # Refresh remove button
        if "removable" in old_app_data and "removable" not in new_app_data:
            # remove button
            self._remove_btn.destroy()
            self._remove_btn = None
        if "removable" not in old_app_data and "removable" in new_app_data:
            # add button
            self._setup_remove_button()

        # Refresh desktop button
        if (("_install" in old_app_data and "_install" in new_app_data and
            old_app_data["_install"] == new_app_data["_install"]) or
            "_install" not in old_app_data and "_install" not in new_app_data) and \
            (("desktop" in old_app_data and "desktop" in new_app_data and
             old_app_data["desktop"] == new_app_data["desktop"]) or
             "desktop" not in old_app_data and "desktop" not in new_app_data):
            if self._desktop_btn:
                self._desktop_btn.refresh()
            else:
                self._setup_desktop_button()
        else:
            if self._desktop_btn:
                self._desktop_btn.destroy()
            self._setup_desktop_button()

        self.show_all()

    def _set_title(self, app):
        name = app["title"]
        if "_install" in app:
            name = "Install {}".format(name)

        self._app_name.set_text(name)

    def _set_tagline(self, app):
        tagline = app['tagline']
        if tagline > 70:
            tagline = tagline[0:70]

        self._app_desc.set_text(tagline)

    def _launch_app(self, cmd, args):
        try:
            os.execvp(cmd, [cmd] + args)
        except:
            pass

        # The execvp should not return, so if we reach this point,
        # there was an error.
        message = KanoDialog(
            _("Error"),
            _("Unable to start the application."),
            {
                _("OK"): {
                    "return_value": 0,
                    "color": "red"
                }
            },
            parent_window=self._window
        )
        message.run()

    def _setup_desc_button(self):
        if self._more_btn:
            return

        self._more_btn = more_btn = Gtk.Button(hexpand=False)
        more = Gtk.Image.new_from_file("{}/icons/more.png".format(media_dir()))
        more_btn.set_image(more)
        more_btn.props.margin_right = 21
        more_btn.get_style_context().add_class('more-button')
        more_btn.connect("clicked", self._show_more_cb)
        more_btn.set_tooltip_text(_("More information"))
        more_btn.connect("realize", self._set_cursor_to_hand_cb)
        self._entry.pack_start(more_btn, False, False, 0)

        if self._update_btn:
            self._entry.reorder_child(more_btn, 3)
        else:
            self._entry.reorder_child(more_btn, 2)

    def _setup_remove_button(self):
        if self._remove_btn:
            return

        self._remove_btn = remove_btn = Gtk.Button(hexpand=False)
        bin_open_img = "{}/icons/trashbin-open.png".format(media_dir())
        self._res_bin_open = Gtk.Image.new_from_file(bin_open_img)
        bin_closed_img = "{}/icons/trashbin-closed.png".format(media_dir())
        self._res_bin_closed = Gtk.Image.new_from_file(bin_closed_img)
        remove_btn.set_image(self._res_bin_closed)
        remove_btn.props.margin_right = 21
        remove_btn.get_style_context().add_class('more-button')
        remove_btn.connect("clicked", self._uninstall_cb)
        remove_btn.set_tooltip_text(_("Remove"))
        remove_btn.connect("realize", self._set_cursor_to_hand_cb)
        remove_btn.connect("enter-notify-event", self._open_bin_cb)
        remove_btn.connect("leave-notify-event", self._close_bin_cb)
        self._entry.pack_start(remove_btn, False, False, 0)

        if self._update_btn and self._more_btn:
            self._entry.reorder_child(remove_btn, 4)
        elif self._update_btn or self._more_btn:
            self._entry.reorder_child(remove_btn, 3)
        else:
            self._entry.reorder_child(remove_btn, 2)

    def _setup_desktop_button(self):
        self._desktop_btn = None
        if "_install" not in self._app and \
           ("desktop" not in self._app or self._app["desktop"]):
            if os.path.exists(KDESK_EXEC):
                self._desktop_btn = DesktopButton(self._app, self._apps)
                self._entry.pack_start(self._desktop_btn, False, False, 0)

    def _setup_update_button(self):
        if self._update_btn:
            return

        self._update_btn = update_btn = Gtk.Button(hexpand=False)
        img = Gtk.Image.new_from_file("{}/icons/update.png".format(media_dir()))
        update_btn.set_image(img)
        update_btn.props.margin_right = 21
        update_btn.get_style_context().add_class('more-button')
        update_btn.connect("clicked", self._update_cb)
        update_btn.set_tooltip_text(_("Update app"))
        update_btn.connect("realize", self._set_cursor_to_hand_cb)
        self._entry.pack_start(update_btn, False, False, 0)
        self._entry.reorder_child(update_btn, 2)

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
                _("OK, GOT IT"): {
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
            title_text=_("Removing {}").format(self._app["title"]),
            description_text=_("This application will be uninstalled and " +
                             "removed from apps. Do you wish to proceed?"),
            button_dict={
                _("YES"): {
                    "return_value": 0
                },
                _("NO"): {
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

        prompt = _("Uninstalling {}").format(self._app["title"])
        pw = get_sudo_password(prompt, self._window)
        if pw is None:
            return

        self._window.blur()
        self._window.get_window().set_cursor(Gdk.Cursor(Gdk.CursorType.WATCH))
        while Gtk.events_pending():
            Gtk.main_iteration()

        success = uninstall_packages(self._app, pw)
        if success:
            remove_from_desktop(self._app)
            uninstall_link_and_icon(self._app["slug"], pw)

        self._apps.remove_app(self._app)

        self._window.get_window().set_cursor(Gdk.Cursor(Gdk.CursorType.ARROW))
        self._window.unblur()

    def _install_cb(self):
        self._install_app()

    def _update_cb(self, widget):
        confirmation = KanoDialog(
            title_text=_("Updating {}").format(self._app["title"]),
            description_text=_("This application will be updated " +
                             "Do you wish to proceed?"),
            button_dict={
                _("YES"): {
                    "return_value": 0
                },
                _("NO"): {
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

        self._install_app(report_install=False)

    def _install_app(self, report_install=True):
        installer = AppInstaller(self._app['id'], self._apps, None,
                                 self._window)
        installer.set_report_install(report_install)
        if not installer.install():
            return

        # We need to reload the application information, readd it to
        # the desktop and send an update to the parent object.
        new_app = load_from_app_file(installer.get_loc())
        self._app['origin'] = new_app['origin']
        remove_from_desktop(self._app)
        self._apps.update_app(new_app)

        if new_app.get('desktop'):
            add_to_desktop(new_app)

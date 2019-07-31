# MainWindow.py
#
# Copyright (C) 2014 - 2018 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPLv2
#
# A class that handles app installations
#

import json
import os

from gi import require_version
require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk

from kano_apps.AppManage import install_app, download_app, AppDownloadError, \
    install_link_and_icon
from kano_apps.DesktopManage import add_to_desktop
from kano_apps.AppData import load_from_app_file, is_app_installed
from kano_apps.UIElements import get_sudo_password
from kano.gtk3.kano_dialog import KanoDialog
from kano_world.connection import request_wrapper
from kano_world.functions import get_glob_session


class AppInstaller:
    def __init__(self, id_or_slug, apps, pw=None, parent_win=None):
        self._handle = id_or_slug
        self._win = parent_win
        self._apps = apps

        self._tmp_data_file = None
        self._tmp_icon_file = None
        self._loc = None
        self._pw = pw

        self._icon_only = False
        self._add_to_desktop = True
        self._check_if_installed = False

    def install(self):
        if self._win is not None:
            self._win.blur()
            self._win.get_window().set_cursor(Gdk.Cursor(Gdk.CursorType.WATCH))

        if not self._download_app():
            return self._end(False)

        if self._check_if_installed:
            if not self._installed_check():
                return self._end(False)

        if not self._get_sudo_pw():
            return self._end(False)

        # Prevent the user escaping with the home button
        os.system('kano-home-button-visible no')

        # Make sure the dialogs are gone before installing
        while Gtk.events_pending():
            Gtk.main_iteration()

        rv = self._install()

        # Should be safe to bail at this point
        os.system('kano-home-button-visible yes')
        return self._end(rv)

    def set_icon_only(self, v):
        self._icon_only = bool(v)

    def set_add_to_desktop(self, v):
        self._add_to_desktop = bool(v)

    def set_check_if_installed(self, v):
        self._check_if_installed = v

    def get_loc(self):
        return self._loc

    def get_sudo_pw(self):
        return self._pw

    # Private methods onwards
    def _end(self, rv=True):
        if self._win is not None:
            self._win.get_window().set_cursor(Gdk.Cursor(Gdk.CursorType.ARROW))
            self._win.unblur()

        return rv

    def _download_app(self):
        try:
            app_data_file, app_icon_file = download_app(self._handle)
            self._tmp_data_file = app_data_file
            self._tmp_icon_file = app_icon_file
        except AppDownloadError as err:
            head = _("Unable to download the application")
            dialog = KanoDialog(
                head, unicode(err),
                {
                    _("OK"): {
                        "return_value": 0
                    },
                },
                parent_window=self._win
            )
            dialog.run()
            del dialog
            return False

        self._app = load_from_app_file(self._tmp_data_file, False)

        return True

    def _installed_check(self):
        if is_app_installed(self._app):
            head = _("{} is already installed").format(self._app["title"])
            desc = _("Would you like to update it?")
            dialog = KanoDialog(
                head, desc,
                {
                    _("YES"): {
                        "return_value": 0
                    },
                    _("NO"): {
                        "return_value": -1
                    }
                },
                parent_window=self._win
            )
            rv = dialog.run()
            del dialog
            return rv == 0

        return True

    def _get_sudo_pw(self):
        if self._pw is None:
            self._pw = get_sudo_password(_("Installing {}").format(self._app["title"]))
            return self._pw is not None

        return True

    def _install(self):
        success = True
        if not self._icon_only:
            success = install_app(self._app, self._pw)

        if success:
            # write out the tmp json
            with open(self._tmp_data_file, "w") as f:
                f.write(json.dumps(self._app))

            self._loc = install_link_and_icon(self._app['slug'],
                                              self._tmp_data_file,
                                              self._tmp_icon_file,
                                              self._pw)

            if not self._icon_only and self._add_to_desktop:
                add_to_desktop(self._app)

            head = _("Done!")
            message = _(
                "{} installed successfully! "
                "Look for it in the Apps launcher."
            ).format(self._app["title"])
        else:
            head = _("Installation failed")
            message = _(
                "{} cannot be installed at "
                "the moment. Please make sure your kit is connected "
                "to the internet and there is enough space left on "
                "your card."
            ).format(self._app["title"])

        dialog = KanoDialog(
            head,
            message,
            {
                _("OK"): {
                    "return_value": 0
                },
            },
        )
        dialog.run()
        del dialog

        return success

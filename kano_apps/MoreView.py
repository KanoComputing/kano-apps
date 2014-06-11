# UIElements.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# Different parts of the app's UI

import os
import re
from gi.repository import Gtk, Gdk
from kano.gtk3.scrolled_window import ScrolledWindow

from kano_apps.Media import media_dir, get_app_icon

try:
    from kano_video.player import play_video
except:
    pass


class MoreView(Gtk.EventBox):
    _KDESK_DIR = '~/.kdesktop/'
    _KDESK_EXEC = '/usr/bin/kdesk'

    def __init__(self, app, main_win):
        Gtk.EventBox.__init__(self, hexpand=True, vexpand=False)
        self.get_style_context().add_class('grey-bg')

        self._app = app
        self._window = main_win

        self._box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL,
                            vexpand=True, spacing=0)
        self._box.props.margin_top = 25
        self._box.props.margin_left = 80
        self._box.props.margin_right = 100
        self._box.props.margin_bottom = 100

        content_box = self._initialise_content()
        self._box.pack_start(content_box, True, True, 0)

        self.add(self._box)

    def _initialise_content(self):
        content_box = Gtk.EventBox(vexpand=False, hexpand=False)
        content_box.get_style_context().add_class('help-box')

        content_grid = Gtk.Grid(vexpand=False, hexpand=False)
        content_grid.props.margin = 25
        content_grid.props.margin_left = 15
        content_grid.props.margin_right = 15

        icon = get_app_icon(self._app["Icon"])
        icon.props.margin_right = 10
        icon_alignment = Gtk.Alignment(xalign=0.5, yalign=0, xscale=0, yscale=0)
        icon_alignment.add(icon)
        content_grid.attach(icon_alignment, 0, 0, 1, 2)

        title = Gtk.Label(self._app['Name'])
        title.get_style_context().add_class('help-title')
        title.set_justify(Gtk.Justification.LEFT)
        title_alignment = Gtk.Alignment(xalign=0, yalign=0, xscale=0, yscale=0)
        title_alignment.add(title)
        content_grid.attach(title_alignment, 1, 0, 1, 1)

        if 'Help' in self._app:
            help_text = Gtk.Label(re.sub(r'\\n', "\n", self._app['Help']))
            help_text.get_style_context().add_class('help-text')
            help_text.set_justify(Gtk.Justification.FILL)
            help_text.props.valign = Gtk.Align.START
            help_text.props.halign = Gtk.Align.START
            help_text.set_line_wrap(True)
            help_text.props.margin_right = 15

            sw = ScrolledWindow(hexpand=True)
            sw.add_with_viewport(help_text)
            sw.props.margin_top = 10
            sw.props.margin_bottom = 15

            content_grid.attach(sw, 1, 1, 1, 1)
            sw.set_size_request(-1, 250)
        else:
            help_text = Gtk.Label(self._app['Comment[en_GB]'])
            help_text.get_style_context().add_class('help-text')
            help_text.set_justify(Gtk.Justification.LEFT)
            help_text.props.valign = Gtk.Align.START
            help_text.props.halign = Gtk.Align.START
            help_text.set_line_wrap(True)
            help_text.props.margin_right = 15
            help_text.props.margin_left = 3
            content_grid.attach(help_text, 1, 1, 1, 1)

        content_grid.attach(self._initialise_buttons(), 1, 2, 1, 1)

        content_box.add(content_grid)

        alignment = Gtk.Alignment(xalign=0.5, yalign=0, xscale=1, yscale=0)
        alignment.add(content_box)
        return alignment

    def _initialise_buttons(self):
        buttons = Gtk.Box(spacing=15)
        buttons.props.margin_top = 10

        kdesk_dir = os.path.expanduser('~/.kdesktop/')
        file_name = re.sub(' ', '-', self._app["Name"]) + ".lnk"
        on_desktop = os.path.exists(kdesk_dir + file_name)

        if os.path.exists(self._KDESK_EXEC):
            if on_desktop:
                btn_label = 'REMOVE FROM DESKTOP'
                btn_style = 'cancel_button'
                click_cb = self._desktop_toggle_rm
            else:
                btn_label = 'ADD TO DESKTOP'
                btn_style = 'desktop_toggle_button'
                click_cb = self._desktop_toggle_add

            desktop_toggle = Gtk.Button(btn_label)
            desktop_toggle.set_size_request(225, 44)
            desktop_toggle.modify_fg(Gtk.StateFlags.NORMAL, Gdk.color_parse("white"))
            desktop_toggle_style = desktop_toggle.get_style_context()
            desktop_toggle_style.add_class(btn_style)
            desktop_toggle_style.add_class('no_border')
            desktop_toggle.connect('clicked', click_cb)

            buttons.pack_start(desktop_toggle, False, False, 0)

        if 'Video' in self._app:
            has_video = True
            try:
                play_video
            except:
                has_video = False

            if has_video:
                video = Gtk.Button('WATCH VIDEO')
                video.set_size_request(150, 44)
                video.modify_fg(Gtk.StateFlags.NORMAL, Gdk.color_parse("white"))
                video_style = video.get_style_context()
                video_style.add_class('orange_button')
                video_style.add_class('no_border')
                video.connect('clicked', self._video_clicked)

                buttons.pack_start(video, False, False, 0)

        return buttons

    def _video_clicked(self, event):
        play_video(None, None, self._app['Video'], True)

    def _desktop_toggle_add(self, event):
        self._create_kdesk_icon()

        os.system('kdesk -r')
        self._window.show_more_view(self._app)

    def _desktop_toggle_rm(self, event):
        os.unlink(self._get_kdesk_icon_path())

        os.system('kdesk -r')
        self._window.show_more_view(self._app)

    def _get_kdesk_icon_path(self):
        kdesk_dir = os.path.expanduser(self._KDESK_DIR)
        return kdesk_dir + re.sub(' ', '-', self._app["Name"]) + ".lnk"

    def _create_kdesk_icon(self):
        kdesk_entry = 'table Icon\n'
        kdesk_entry += '  Caption:\n'
        kdesk_entry += '  AppID:\n'
        kdesk_entry += '  Command: {}\n'.format(self._app["Exec"])
        kdesk_entry += '  Singleton: true\n'
        kdesk_entry += '  Icon: {}\n'.format(self._app["Icon"])
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

# AddDialog.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#

import os
import re
from gi.repository import Gtk, GdkPixbuf

from kano_apps.Media import media_dir, get_app_icon
from kano.gtk3.buttons import KanoButton
from kano.gtk3.cursor import attach_cursor_events


class AddDialog(Gtk.EventBox):
    def __init__(self, main_win):
        Gtk.EventBox.__init__(self, hexpand=True, vexpand=True)
        self._box = Gtk.Box(hexpand=True, vexpand=True,
                            halign=Gtk.Align.CENTER, valign=Gtk.Align.CENTER,
                            orientation=Gtk.Orientation.VERTICAL, spacing=0)

        self._icon_path = 'exec'
        self._window = main_win

        self.get_style_context().add_class('white-bg')

        self._init_header()
        self._init_form()
        self._init_buttons()
        self.add(self._box)

    def _init_header(self):
        title = Gtk.Label('Add application')
        description = Gtk.Label('Add your own application to Apps')

        title_style = title.get_style_context()
        title_style.add_class('title')

        description_style = description.get_style_context()
        description_style.add_class('description')

        box = Gtk.Box(spacing=5, orientation=Gtk.Orientation.VERTICAL,
                      halign=Gtk.Align.CENTER, valign=Gtk.Align.CENTER)
        box.pack_start(title, False, False, 0)
        box.pack_start(description, False, False, 0)
        self._box.pack_start(box, False, False, 0)

    def _init_form(self):
        form = Gtk.Grid(row_spacing=22, column_spacing=22)

        icon = get_app_icon(media_dir() + "icons/add-icon.png", 132)
        icon.props.valign = Gtk.Align.START
        self._icon = icon

        icon_button = Gtk.EventBox()
        icon_button.add(icon)
        icon_button.connect('button-release-event', self._icon_click)
        attach_cursor_events(icon_button)
        form.attach(icon_button, 0, 0, 1, 3)

        name = Gtk.Entry()
        name.props.placeholder_text = "Application's name"
        name.set_size_request(280, 44)
        self._name = name
        form.attach(name, 1, 0, 1, 1)

        desc = Gtk.Entry()
        desc.props.placeholder_text = "Description"
        desc.set_size_request(280, 44)
        self._desc = desc
        form.attach(desc, 1, 1, 1, 1)

        cmd = Gtk.Entry()
        cmd.props.placeholder_text = "Command"
        cmd.set_size_request(280, 44)
        self._cmd = cmd
        form.attach(cmd, 1, 2, 1, 1)

        self._box.pack_start(form, False, False, 40)

    def _init_buttons(self):
        container = Gtk.Box(spacing=25, halign=Gtk.Align.CENTER)

        cancel = KanoButton(text='CANCEL', color="red")
        cancel.set_size_request(124, 44)
        cancel.connect('clicked', self._cancel_click)

        add = KanoButton('ADD APPLICATION')
        add.set_size_request(174, 44)
        add.connect('clicked', self._add_click)

        container.pack_start(cancel, False, False, 0)
        container.pack_start(add, False, False, 0)

        self._box.pack_start(container, False, False, 40)

    def _cancel_click(self, event):
        self._window.show_apps_view()

    def _add_click(self, event):
        self._new_user_dentry(self._name.get_text(),
                              self._desc.get_text(),
                              self._cmd.get_text(),
                              self._icon_path)

    def _new_user_dentry(self, name, desc, cmd, icon_path):
        dentry = '[Desktop Entry]\n'
        dentry += 'Encoding=UTF-8\n'
        dentry += 'Type=Application\n'
        dentry += 'Name={}\n'.format(name)
        dentry += 'Name[en_GB]={}\n'.format(name)
        dentry += 'Icon={}\n'.format(icon_path)
        dentry += 'Exec={}\n'.format(cmd)
        dentry += 'Categories=User;\n'
        dentry += 'Comment[en_GB]={}'.format(desc)

        apps_dir = os.path.expanduser('~/.apps/')
        if not os.path.exists(apps_dir):
            os.makedirs(apps_dir)

        file_name = re.sub(' ', '-', name)
        f = open(apps_dir + name, 'w')
        f.write(dentry)
        f.close()

        self._window.show_apps_view()

    def _icon_click(self, ebox, event):
        self._window._top_bar.enable_prev()

        dialog = Gtk.FileChooserDialog("Please choose an icon", self._window,
                                       Gtk.FileChooserAction.OPEN,
                                       (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                                        Gtk.STOCK_OPEN, Gtk.ResponseType.OK))

        # Set up file filters
        filter_text = Gtk.FileFilter()
        filter_text.set_name("Image files")
        filter_text.add_mime_type("image/png")
        filter_text.add_mime_type("image/jpeg")
        filter_text.add_mime_type("image/svg+xml")
        filter_text.add_mime_type("image/gif")
        dialog.add_filter(filter_text)

        filter_any = Gtk.FileFilter()
        filter_any.set_name("Any files")
        filter_any.add_pattern("*")
        dialog.add_filter(filter_any)

        dialog.set_current_folder(os.path.expanduser('~'))

        response = dialog.run()

        if response == Gtk.ResponseType.OK:
            self._icon_path = dialog.get_filename()

            pb = GdkPixbuf.Pixbuf.new_from_file_at_size(self._icon_path,
                                                        132, 132)
            self._icon.set_from_pixbuf(pb)
        elif response == Gtk.ResponseType.CANCEL:
            pass

        dialog.destroy()


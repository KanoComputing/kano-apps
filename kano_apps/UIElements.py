# UIElements.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# Different parts of the app's UI

import os
import re
from gi.repository import Gtk, Gdk, Pango, GdkPixbuf

from kano_apps import Media
from kano_apps.AppData import parse_command, get_applications
from kano_apps.Media import media_dir, get_app_icon

class TopBar(Gtk.EventBox):
    _TOP_BAR_HEIGHT = 44

    def __init__(self):
        Gtk.EventBox.__init__(self)
        self.get_style_context().add_class('top_bar_container')

        box = Gtk.Box()
        box.set_size_request(-1, self._TOP_BAR_HEIGHT)

        self._header = Gtk.Label('Apps', halign=Gtk.Align.CENTER,
                                           valign=Gtk.Align.CENTER,
                                           hexpand=True)
        box.pack_start(self._header, True, True, 0)

        self._header.modify_font(Pango.FontDescription('Bariol 13'))
        self._header.get_style_context().add_class('header')

        # Close button
        cross_icon = Media.get_ui_icon('cross')

        self._close_button = Gtk.Button()
        self._close_button.set_image(cross_icon)
        self._close_button.props.margin_right = 2
        self._close_button.set_can_focus(False)
        self._close_button.get_style_context().add_class('top_bar_button')
        self._close_button.get_style_context().add_class('no_border')

        self._close_button.connect('clicked', self._close_button_click)
        self._close_button.connect('enter-notify-event',
                                   self._close_button_mouse_enter)
        self._close_button.connect('leave-notify-event',
                                   self._close_button_mouse_leave)

        box.pack_start(self._close_button, False, False, 0)

        self.add(box)

    def _close_button_mouse_enter(self, button, event):
        # Change the cursor to hour Glass
        cursor = Gdk.Cursor.new(Gdk.CursorType.HAND1)
        self.get_root_window().set_cursor(cursor)

    def _close_button_mouse_leave(self, button, event):
        # Set the cursor to normal Arrow
        cursor = Gdk.Cursor.new(Gdk.CursorType.ARROW)
        self.get_root_window().set_cursor(cursor)

    def _close_button_click(self, event):
        cursor = Gdk.Cursor.new(Gdk.CursorType.ARROW)
        self.get_root_window().set_cursor(cursor)
        Gdk.flush()

        Gtk.main_quit()

class AppGridEntry(Gtk.EventBox):
    def __init__(self, label, desc, icon_loc, window):
        Gtk.EventBox.__init__(self)

        self._window = window

        self._entry = entry = Gtk.Grid()
        entry.set_row_spacing(0)

        self._icon = icon = Media.get_app_icon(icon_loc)
        icon.props.margin = 15
        entry.attach(icon, 0, 0, 1, 3)

        self._app_name = app_name = Gtk.Label(label, halign=Gtk.Align.START,
                                    valign=Gtk.Align.CENTER,
                                    hexpand=True)
        app_name.get_style_context().add_class('app_name')
        app_name.modify_font(Pango.FontDescription('Bariol bold 18'))
        app_name.props.margin_top = 25

        entry.attach(app_name, 1, 0, 1, 1)

        self._app_desc = app_desc = Gtk.Label(desc,
                             halign=Gtk.Align.START,
                             valign=Gtk.Align.START,
                             hexpand=True)
        app_desc.get_style_context().add_class('app_desc')
        app_desc.modify_font(Pango.FontDescription('Bariol 12'))
        app_desc.props.margin_bottom = 25
        entry.attach(app_desc, 1, 1, 1, 1)

        self._app_name.props.margin_top = 14
        self._app_desc.props.margin_bottom = 0

        self._links = Gtk.HBox(False, 0)
        self._links.props.margin_bottom = 14
        entry.attach(self._links, 1, 2, 1, 1)
        self._links_count = 0

        self.add(entry)
        self.connect("enter-notify-event", self._mouse_enter)
        self.connect("leave-notify-event", self._mouse_leave)
        self.connect("button-release-event", self._mouse_click)

    def _add_link(self, label, callback):
        ebox = Gtk.EventBox()
        link = Gtk.Label(label, halign=Gtk.Align.START,
                         valign=Gtk.Align.START)
        link.get_style_context().add_class('app_link')
        link.modify_font(Pango.FontDescription('Bariol bold 12'))
        ebox.add(link)

        if self._links_count:
            spacer = Gtk.Label("|", halign=Gtk.Align.START,
                               valign=Gtk.Align.START)
            spacer.get_style_context().add_class('app_link_spacer')
            self._links.pack_start(spacer, False, False, 2)

        self._links.pack_start(ebox, False, False, 2)

        self._links_count += 1

        ebox.connect("button-release-event", callback)
        ebox.connect("enter-notify-event", self._mouse_enter)
        ebox.connect("leave-notify-event", self._mouse_leave)

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

    def _mouse_enter(self, ebox, event):
        # Change the cursor to hour Glass
        cursor = Gdk.Cursor.new(Gdk.CursorType.HAND1)
        self.get_root_window().set_cursor(cursor)

    def _mouse_leave(self, ebox, event):
        # Set the cursor to normal Arrow
        cursor = Gdk.Cursor.new(Gdk.CursorType.ARROW)
        self.get_root_window().set_cursor(cursor)

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
        cursor = Gdk.Cursor.new(Gdk.CursorType.ARROW)
        self.get_root_window().set_cursor(cursor)
        Gdk.flush()

        more_view = MoreView(self._app, self._window)
        self._window.get_main_area().set_contents(more_view)
        return True

    def _mouse_click(self, ebox, event):
        cursor = Gdk.Cursor.new(Gdk.CursorType.ARROW)
        self.get_root_window().set_cursor(cursor)
        Gdk.flush()

        self._launch_app(self._cmd['cmd'], self._cmd['args'])

class UserApp(SystemApp):
    def __init__(self, app, window):
        SystemApp.__init__(self, app, window)

        self._icon_source = app['icon_source']

        self._add_link("Remove", self._remove_mouse_click)

    def _remove_mouse_click(self, widget, event):
        cursor = Gdk.Cursor.new(Gdk.CursorType.ARROW)
        self.get_root_window().set_cursor(cursor)
        Gdk.flush()

        os.unlink(self._icon_source)
        apps = Apps(get_applications(), self._window)
        self._window.get_main_area().set_contents(apps)
        apps.set_current_page(-1)
        return True

class UninstallableApp(SystemApp):
    def __init__(self, app, window):
        SystemApp.__init__(self, app, window)

        # Deal with the params placeholder
        uninstall_cmd = re.sub(r'\%[pP]', 'uninstall', uninstall_cmd)
        self._uninstall_cmd = parse_command(uninstall_cmd)

        self._add_link("Uninstall", self._remove_mouse_click)

    def _remove_mouse_click(self, widget, event):
        cursor = Gdk.Cursor.new(Gdk.CursorType.ARROW)
        self.get_root_window().set_cursor(cursor)
        Gdk.flush()

        self._launch_app(self._uninstall_cmd['cmd'], self._uninstall_cmd['args'])

class AddButton(AppGridEntry):
    def __init__(self, window):
        self._window = window
        AppGridEntry.__init__(self, 'Add application',
                              'Want to access more apps?',
                              media_dir() + 'icons/add.png', window)

    def _mouse_click(self, ebox, event):
        cursor = Gdk.Cursor.new(Gdk.CursorType.ARROW)
        self.get_root_window().set_cursor(cursor)
        Gdk.flush()

        # Todo remove itself from the scroll area
        dialog = AddDialog(self._window)
        self._window.get_main_area().set_contents(dialog)


class Contents(Gtk.EventBox):
    def __init__(self, win):
        Gtk.EventBox.__init__(self, hexpand=True, vexpand=True)

        style = self.get_style_context()
        style.add_class('contents')

        self._current = None
        self._win = win

    def get_window(self):
        return self._win

    def set_contents(self, obj):
        for w in self.get_children():
            self.remove(w)

        self.add(obj)
        obj.show_all()

class Apps(Gtk.Notebook):
    def __init__(self, apps, main_win):
        Gtk.Notebook.__init__(self)

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
        tools_label.modify_font(Pango.FontDescription('Bariol bold'))
        self.append_page(tools, tools_label)

        extras_label = Gtk.Label("EXTRAS")
        extras_label.modify_font(Pango.FontDescription('Bariol bold'))
        self.append_page(extras, extras_label)

        user_label = Gtk.Label("USER")
        user_label.modify_font(Pango.FontDescription('Bariol bold'))
        self.append_page(user, user_label)

class AppGrid(Gtk.EventBox):
    def __init__(self, apps, main_win):
        Gtk.EventBox.__init__(self, hexpand=True, vexpand=True)

        self._sw = Gtk.ScrolledWindow(hexpand=True, vexpand=True)

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

class AddDialog(Gtk.EventBox):
    def __init__(self, main_win):
        Gtk.EventBox.__init__(self, hexpand=True, vexpand=True)
        self._box = Gtk.Box(hexpand=True, vexpand=True,
                         halign=Gtk.Align.CENTER, valign=Gtk.Align.CENTER,
                         orientation=Gtk.Orientation.VERTICAL, spacing=0)

        self._icon_file = 'exec'
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
        icon_button.connect('enter-notify-event', self._button_mouse_enter)
        icon_button.connect('leave-notify-event', self._button_mouse_leave)
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

        cancel = Gtk.Button('CANCEL')
        cancel.set_size_request(124, 44)
        cancel.modify_fg(Gtk.StateFlags.NORMAL, Gdk.color_parse("white"))
        cancel_style = cancel.get_style_context()
        cancel_style.add_class('cancel_button')
        cancel_style.add_class('no_border')
        cancel.connect('clicked', self._cancel_click)
        cancel.connect('enter-notify-event', self._button_mouse_enter)
        cancel.connect('leave-notify-event', self._button_mouse_leave)

        add = Gtk.Button('ADD APPLICATION')
        add.set_size_request(174, 44)
        add_style = add.get_style_context()
        add_style.add_class('add_button')
        add_style.add_class('no_border')
        add.connect('clicked', self._add_click)
        add.connect('enter-notify-event', self._button_mouse_enter)
        add.connect('leave-notify-event', self._button_mouse_leave)

        container.pack_start(cancel, False, False, 0)
        container.pack_start(add, False, False, 0)

        self._box.pack_start(container, False, False, 40)

    def _cancel_click(self, event):
        self._reset_cursor()

        apps = Apps(get_applications(), self._window)
        self._window.get_main_area().set_contents(apps)
        apps.set_current_page(-1)

    def _add_click(self, event):
        self._reset_cursor()
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

        apps = Apps(get_applications(), self._window)
        self._window.get_main_area().set_contents(apps)
        apps.set_current_page(-1)

    def _icon_click(self, ebox, event):
        self._reset_cursor()

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

    def _button_mouse_enter(self, button, event):
        # Change the cursor to hour Glass
        cursor = Gdk.Cursor.new(Gdk.CursorType.HAND1)
        self.get_root_window().set_cursor(cursor)

    def _button_mouse_leave(self, button, event):
        # Set the cursor to normal Arrow
        cursor = Gdk.Cursor.new(Gdk.CursorType.ARROW)
        self.get_root_window().set_cursor(cursor)

    def _reset_cursor(self):
        cursor = Gdk.Cursor.new(Gdk.CursorType.ARROW)
        self.get_root_window().set_cursor(cursor)
        Gdk.flush()


class MoreView(Gtk.EventBox):
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

        back = Gtk.Button()
        back.get_style_context().add_class('no_border')
        back.set_image(get_app_icon(media_dir() + 'icons/back.png', 24))
        back_alignment = Gtk.Alignment(xalign=0.5, yalign=0, xscale=0, yscale=0)
        back_alignment.add(back)
        back.connect('clicked', self._back_click)
        back.connect('enter-notify-event', self._button_mouse_enter)
        back.connect('leave-notify-event', self._button_mouse_leave)
        self._box.pack_start(back_alignment, False, False, 10)

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
            help_text = Gtk.Label(self._app['Help'])
            help_text.get_style_context().add_class('help-text')
            help_text.set_justify(Gtk.Justification.FILL)
            help_text.props.valign = Gtk.Align.START
            help_text.props.halign = Gtk.Align.START
            help_text.set_line_wrap(True)
            help_text.props.margin_right = 15

            sw = Gtk.ScrolledWindow(hexpand=True)
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
        buttons = Gtk.Box()
        buttons.props.margin_top = 10

        kdesk_dir = os.path.expanduser('~/.kdesktop/')
        file_name = re.sub(' ', '-', self._app["Name"]) + ".lnk"
        on_desktop = os.path.exists(kdesk_dir + file_name)

        if on_desktop:
            btn_label = 'REMOVE FROM DESKTOP'
            btn_style = 'cancel_button'
            click_cb = self._desktop_toggle_rm
        else:
            btn_label = 'ADD TO DESKTOP'
            btn_style = 'desktop_toggle_button'
            click_cb = self._desktop_toggle_add

        desktop_toggle = Gtk.Button(btn_label)
        desktop_toggle.set_size_request(210, 44)
        desktop_toggle.modify_fg(Gtk.StateFlags.NORMAL, Gdk.color_parse("white"))
        desktop_toggle_style = desktop_toggle.get_style_context()
        desktop_toggle_style.add_class(btn_style)
        desktop_toggle_style.add_class('no_border')
        desktop_toggle.connect('clicked', click_cb)
        desktop_toggle.connect('enter-notify-event', self._button_mouse_enter)
        desktop_toggle.connect('leave-notify-event', self._button_mouse_leave)

        buttons.pack_start(desktop_toggle, False, False, 0)

        return buttons
        

    def _desktop_toggle_add(self, event):
        self._reset_cursor()

        self._create_desktop_icon()

    def _desktop_toggle_rm(self, event):
        self._reset_cursor()


    def _back_click(self, event):
        self._reset_cursor()

        apps = Apps(get_applications(), self._window)
        self._window.get_main_area().set_contents(apps)

    def _create_desktop_icon(self):
        kdesk_entry = 'table Icon\n'
        kdesk_entry += '  Caption:\n'
        kdesk_entry += '  AppId: {}\n'.format(self._app["Name"])
        kdesk_entry += '  Command: {}\n'.format(self._app["Exec"])
        kdesk_entry += '  Singleton: true\n'
        kdesk_entry += '  Icon: {}\n'.format(self._app["Icon"])
        kdesk_entry += '  IconHover: {}\n'.format(self._app["Icon"])
        kdesk_entry += '  HoverXoffset: 0\n'
        kdesk_entry += '  Relative-to: grid\n'
        kdesk_entry += '  X: auto\n'
        kdesk_entry += '  Y: auto\n'
        kdesk_entry += 'end\n'

        kdesk_dir = os.path.expanduser('~/.kdesktop/')
        if not os.path.exists(kdesk_dir):
            os.makedirs(kdesk_dir)

        file_name = re.sub(' ', '-', self._app["Name"])
        f = open(kdesk_dir + file_name + '.lnk', 'w')
        f.write(kdesk_entry)
        f.close()

        os.system('kdesk -r')
        more_view = MoreView(self._app, self._window)
        self._window.get_main_area().set_contents(more_view)

    def _icon_click(self, ebox, event):
        self._reset_cursor()

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

    def _button_mouse_enter(self, button, event):
        # Change the cursor to hour Glass
        cursor = Gdk.Cursor.new(Gdk.CursorType.HAND1)
        self.get_root_window().set_cursor(cursor)

    def _button_mouse_leave(self, button, event):
        # Set the cursor to normal Arrow
        cursor = Gdk.Cursor.new(Gdk.CursorType.ARROW)
        self.get_root_window().set_cursor(cursor)

    def _reset_cursor(self):
        cursor = Gdk.Cursor.new(Gdk.CursorType.ARROW)
        self.get_root_window().set_cursor(cursor)
        Gdk.flush()

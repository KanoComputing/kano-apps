#
# steps-dashboard-icons.py
#
# Copyright (C) 2019 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# This module will provide the Gherkin implementation
# to locate the Dashboard icons on the screen.
#

import os
import time

from behave import given, then, when
from qa_tools import hid, findimage

@given(u'that I am in Classic Mode')
def step_classic_mode(context):
    os.system('kano-dashboard-uimode desktop --force 2>/dev/null')
    os.system('pkill -f -9 kano-apps')
    time.sleep(3)

@when(u'I call kano-apps install {} non-gui')
def call_kano_apps_nongui(context, app_name):
    rc = os.system('bin/kano-apps install --no-gui {}'.format(app_name))
    assert rc is 0

@then(u'I see {} installed')
def step_impl(context, app_name):
    app_file = os.path.join('/usr/share/applications', '{}.app'.format(app_name))
    assert os.path.isfile(app_file) is True

@when(u'I start kano-apps')
def step_impl(context):
    rc = os.system('bin/kano-apps > /dev/null 2>&1 &')
    assert rc is 0

@then(u'I see the main dialog with no authentication')
def step_impl(context):
    time.sleep(5)
    icon_filename = 'features/assets/kano-apps-main-screen.png'
    assert (os.path.isfile(icon_filename))
    assert (findimage.is_asset_on_screen(icon_filename) == True)
    os.system('pkill kano-apps')

@when(u'I start kano-apps to install {}')
def step_impl(context, app_name):
    rc = os.system('bin/kano-apps install {} > /dev/null 2>&1 &'.format(app_name))
    assert rc is 0


@then(u'I see the main dialog requesting password')
def step_impl(context):
    time.sleep(10)
    icon_filename = 'features/assets/kano-apps-njam-password.png'
    assert (os.path.isfile(icon_filename))

    j = findimage.get_json_from_screen(icon_filename)
    assert j['maxVal'] > 0.8
    os.system('pkill kano-apps')





    
@then(u'I see the {icon_name} icon on tab {tab_number}')
def find_icon_at_given_tab(context, icon_name, tab_number):

    icon_filename = 'features/assets/kano-apps-main-screen.png'
    assert (os.path.isfile(icon_filename))
    assert (findimage.is_asset_on_screen(icon_filename) == True)

@given(u'that I click on {icon_name}')
def click_on_icon(context, icon_name):
    '''
    Locates the icon_name on the screen, and sends a mouse click event to its center position.
    '''

    # Make sure the application icon is on the screen
    tab_number = 1
    icon_filename = 'features/assets/tab-{}/{}.png'.format(tab_number, icon_name.lower())
    assert (os.path.isfile(icon_filename))

    jdata = findimage.get_json_from_screen(icon_filename)
    assert (jdata['found'] == True)

    # locate the center of the icon to send the click
    click_x = jdata['x'] + (jdata['width'] / 2)
    click_y = jdata['y'] + (jdata['height'] / 2)
    assert (hid.mouse_move (click_x, click_y) == True)
    assert (hid.mouse_left_click() == True)

@then(u'I see {icon_name} running')
def expect_icon_on_screen(context, icon_name):
    '''
    Makes sure that the asset represented by icon_name image file is on the screen
    '''
    app_filename = 'features/assets/open-apps/{}.png'.format(icon_name.lower())
    assert (os.path.isfile(app_filename))

    # expect to see the first screen of the app
    found = False
    for grace in range (1, 15):
        time.sleep(1)

        # TODO: Deal with possible introduction video: omxplayer

        found = findimage.is_asset_on_screen(app_filename)
        if found:
            break

    assert (found == True)

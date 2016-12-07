/**
 * app_grid.qml
 *
 * Copyright (C) 2016 Kano Computing Ltd.
 * License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
 *
 * Panning grid for app entries
 */


import QtQuick 2.3
import Kano.Layouts 1.0 as KanoLayouts

import Kano.Apps 1.0 as KanoApps


Item {
    signal app_launched(string launch_command)
    signal app_hovered(string app)

    property alias grid: grid
    property alias columns: grid.columns
    property alias rows: grid.rows

    anchors.fill: parent

    KanoApps.AppGridLayout {
        id: grid
        onApp_launched: parent.app_launched(launch_command)
        onApp_hovered: parent.app_hovered(app)

        anchors.top: parent.top
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.bottom: page_nav.top
        anchors.topMargin: 0
        anchors.bottomMargin: 5

        control: page_nav
    }


    KanoApps.AppGridControl {
        id: page_nav
        anchors.bottom: parent.bottom
        anchors.horizontalCenter: parent.horizontalCenter
    }
}

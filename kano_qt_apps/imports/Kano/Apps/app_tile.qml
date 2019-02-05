/**
 * app_tile.qml
 *
 * Copyright (C) 2016-2019 Kano Computing Ltd.
 * License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
 *
 * An app entry for the creative apps list
 */


import QtQuick 2.3
import Kano.Components 1.0 as Components
import Kano.Fonts 1.0 as Fonts

Item {
    signal app_launched(string launch_command)
    signal app_hovered(string app)

    property string app: ''
    property alias image_source: icon.image_source
    property string launch_command: ''
    property bool single_app_mode: false
    property string color
    property string hover_colour
    property int cell_spacing: 10

    height: 100
    width: 100

    Components.Tile {
        id: icon
        scale: hovered ? 1.05 : 1.0
        onHoveredChanged: {
            if (!hovered) {
                return;
            }

            app_hovered(app);
        }
        image_source: 'make-apps.png'
        width: height
        anchors.margins: cell_spacing
        anchors.bottomMargin: 10
        anchors.top: parent.top
        anchors.bottom: label.top
        anchors.horizontalCenter: parent.horizontalCenter

        onClicked: parent.app_launched(launch_command)

        // Prevent space triggered launch events
        Keys.onSpacePressed: event.accepted = true
    }

    Item {
        id: label
        anchors.bottom: parent.bottom
        anchors.horizontalCenter: parent.horizontalCenter
        width: app_name.width
        height: app_name.height

        Fonts.H4 {
            id: app_name
            text: app
            anchors.horizontalCenter: parent.horizontalCenter
            anchors.verticalCenter: parent.verticalCenter
        }
    }
}

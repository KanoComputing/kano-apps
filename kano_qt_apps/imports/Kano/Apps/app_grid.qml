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
    }


    Row {
        id: page_nav
        anchors.bottom: parent.bottom
        anchors.horizontalCenter: parent.horizontalCenter
        height: 50

        Repeater {
            model: grid.page_count
            delegate: Item {
                anchors.top: page_nav.top
                anchors.bottom: page_nav.bottom
                width: height

                Rectangle {
                    property bool is_last_page: index + 1 < grid.page_count

                    id: indicator
                    anchors.fill: parent
                    anchors.margins: 5
                    color: 'transparent'
                    border.width: 2
                    radius: 5

                    KanoLayouts.TileGridLayout {
                        id: indicator_apps
                        anchors.fill: parent
                        anchors.margins: 2
                        anchors.leftMargin: anchors.margins * 2
                        anchors.topMargin: anchors.margins * 2
                        rows: 3
                        columns: 3
                        spacing: 5

                        model: 9
                        delegate: Rectangle {
                            property bool space_filled:
                                indicator.is_last_page ||
                                index < (grid.tile_count % grid.page_count)
                            color: space_filled ? 'black' : 'transparent'
                            border.width: 2
                            width: indicator_apps.content_width
                            height: indicator_apps.content_width
                        }
                    }

                    MouseArea {
                        id: indicator_mouse
                        anchors.fill: parent
                        hoverEnabled: true
                        cursorShape: Qt.PointingHandCursor
                        onClicked: grid.set_page(index + 1)
                    }

                    states: [
                        State {
                            name: 'active'
                            when: index == grid.page_index || indicator_mouse.containsMouse
                            PropertyChanges {
                                target: indicator
                                opacity: 1.0
                            }
                        },
                        State {
                            name: 'inactive'
                            when: index != grid.page_index
                            PropertyChanges {
                                target: indicator
                                opacity: 0.5
                            }
                        }
                    ]
                }
            }
        }
    }
}

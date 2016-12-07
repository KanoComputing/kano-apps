/**
 * app_grid_control.qml
 *
 * Copyright (C) 2016 Kano Computing Ltd.
 * License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
 *
 * Control for grid of app entries
 */


import QtQuick 2.3
import Kano.Layouts 1.0 as KanoLayouts

import Kano.Apps 1.0 as KanoApps


Row {
    id: page_nav
    signal change_page(int page)

    property int current_page: 0
    property int page_count: 0
    property int tile_count: 0

    height: 48

    Repeater {
        model: page_count
        delegate: Item {
            property int spacing: 7

            anchors.top: page_nav.top
            anchors.bottom: page_nav.bottom
            width: height + spacing * 2

            Rectangle {
                property bool is_last_page: index + 1 < page_count

                id: indicator

                anchors.fill: parent
                color: 'transparent'
                border.width: 2
                radius: 5
                anchors.leftMargin: spacing
                anchors.rightMargin: spacing

                KanoLayouts.TileGridLayout {
                    id: indicator_apps
                    anchors.fill: parent
                    anchors.margins: 3
                    anchors.leftMargin: anchors.margins * 2
                    anchors.topMargin: anchors.margins + indicator.border.width
                    rows: 3
                    columns: 3
                    spacing: 3

                    model: 9
                    delegate: Rectangle {
                        property bool space_filled:
                            indicator.is_last_page ||
                            index < (tile_count % page_count)
                        color: space_filled ? 'black' : 'transparent'
                        border.width: 1
                        radius: 3
                        width: indicator_apps.content_width
                        height: indicator_apps.content_width
                    }
                }

                MouseArea {
                    id: indicator_mouse
                    anchors.fill: parent
                    hoverEnabled: true
                    cursorShape: Qt.PointingHandCursor
                    onClicked: current_page != index ? change_page(index + 1) : null
                }

                states: [
                    State {
                        name: 'active'
                        when: index == current_page || indicator_mouse.containsMouse
                        PropertyChanges {
                            target: indicator
                            opacity: 1.0
                        }
                    },
                    State {
                        name: 'inactive'
                        when: index != current_page
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

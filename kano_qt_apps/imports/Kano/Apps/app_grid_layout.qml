/**
 * app_grid_layout.qml
 *
 * Copyright (C) 2016-2018 Kano Computing Ltd.
 * License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
 *
 * Grid for app entries
 */


import QtQuick 2.8
import Kano.Layouts 1.0 as KanoLayouts

import Kano.Apps 1.0 as KanoApps


KanoLayouts.TileGridLayout {
    signal app_launched(string launch_command, var data)
    signal app_hovered(string app)


    property int page_index: 0
    property int page: page_index + 1
    readonly property int app_rows: 3
    readonly property int app_columns: 3
    readonly property int view_app_count: app_rows * app_columns
    readonly property int app_count: apps_list.apps.length
    readonly property int page_count: Math.ceil(app_count / 9)


    property var control   // Some KanoApps.AppGridControl

    Binding {
        target: control
        property: 'current_page'
        value: scroll_grid.currentIndex
    }
    Binding {
        target: control
        property: 'page_count'
        value: scroll_grid.page_count
    }
    Binding {
        target: control
        property: 'tile_count'
        value: scroll_grid.view_app_count
    }
    Binding {
        target: control
        property: 'app_count'
        value: scroll_grid.app_count
    }
    Connections {
        target: control

        onChange_page: scroll_grid.set_page(page)
    }

    id: scroll_grid
    spacing: 0

    offset: page_index * tile_count

    function next_page() {
        set_page(page + 1);
    }

    function previous_page() {
        set_page(page - 1);
    }

    function set_page(page_no) {
        page_no--;

        while (currentIndex < page_no) {
            moveCurrentIndexRight();
        }

        while (currentIndex > page_no) {
            moveCurrentIndexLeft();
        }
    }

    rows: 1
    columns: 1

    KanoApps.InstalledAppList {
        id: apps_list
        property bool initialised: false
        function initialise() {
            if (!initialised && scroll_grid.width > 0 && scroll_grid.height > 0) {
                apps_list.update()
                initialised = true;
            }
        }
    }
    model: page_count

    // Rows and columns incorrectly align if the width and height
    // isn't final when they are set
    onWidthChanged: apps_list.initialise()
    onHeightChanged: apps_list.initialise()

    clip: true
    flow: GridView.FlowTopToBottom
    snapMode: GridView.SnapOneRow
    highlightFollowsCurrentItem: true
    highlightRangeMode: GridView.StrictlyEnforceRange
    cellWidth: width

    delegate: KanoLayouts.TileGridLayout {
        id: app_grid
        rows: scroll_grid.app_rows
        columns: scroll_grid.app_columns
        height: scroll_grid.content_height
        width: scroll_grid.content_width
        interactive: false
        tile_model: apps_list.apps.slice(
            tile_count * index, tile_count * (index + 1)
        )
        delegate: KanoApps.AppTile {
            app: modelData.title
            launch_command: modelData.launch_command
            dashboard_less_mode: modelData.dashboard_less_mode
            image_source: modelData.icon
            height: app_grid.content_height
            width: app_grid.content_width
	    property var data: modelData
	    property bool mode: modelData.dashboard_less_mode

            onApp_launched: {
                console.log("Launch command: " + launch_command);
                console.log("Launch Dashboard Less Mode: " + dashboard_less_mode);
                scroll_grid.app_launched(launch_command, {
                    dashboard_less_mode: dashboard_less_mode
                })
	    }
            onApp_hovered: {
                scroll_grid.app_hovered(app)
            }
        }
    }
}

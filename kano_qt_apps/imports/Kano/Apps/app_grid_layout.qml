/**
 * app_grid_layout.qml
 *
 * Copyright (C) 2016 Kano Computing Ltd.
 * License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
 *
 * Grid for app entries
 */


import QtQuick 2.3
import Kano.Layouts 1.0 as KanoLayouts

import Kano.Apps 1.0 as KanoApps


KanoLayouts.TileGridLayout {
    signal app_launched(string launch_command)
    signal app_hovered(string app)

    property int page_index: 0
    property int page: page_index + 1
    readonly property int page_count: Math.ceil(apps_list.apps.length / tile_count)

    id: grid
    spacing: 30

    offset: page_index * tile_count

    function next_page() {
        set_page(page + 1);
    }

    function previous_page() {
        set_page(page - 1);
    }

    function set_page(page_no) {
        page_no--;
        pop_trans.ltr = page_no < page_index;

        page_no = page_no % page_count;
        if (page_no < 0) {
            page_no = page_count + page_no;
        }

        page_index = page_no;
    }

    rows: 3
    columns: 3

    KanoApps.InstalledAppList {
        id: apps_list
        property bool initialised: false
        function initialise() {
            if (!initialised && grid.width > 0 && grid.height > 0) {
                apps_list.update()
                initialised = true;
            }
        }
    }
    tile_model: apps_list.apps

    // Rows and columns incorrectly align if the width and height
    // isn't final when they are set
    onWidthChanged: apps_list.initialise()
    onHeightChanged: apps_list.initialise()

    populate: Transition {
        id: pop_trans
        property point dest: pop_trans.ViewTransition.destination
        property bool ltr: true

        ParallelAnimation {
            NumberAnimation {
                property: 'opacity'
                from: 0.0
                to: 1.0
                duration: 400
            }
            NumberAnimation {
                properties: 'x'
                from: pop_trans.ltr ?
                    pop_trans.dest.x - grid.cellWidth / 2 :
                    pop_trans.dest.x + grid.cellWidth / 2
                duration: 300
            }
        }
    }

    clip: true

    delegate: KanoApps.AppTile {
        app: modelData.title
        launch_command: modelData.launch_command
        image_source: 'qrc:/' + modelData.icon
        height: grid.cellHeight
        width: grid.cellWidth
        onApp_launched: grid.app_launched(launch_command)
        onApp_hovered: grid.app_hovered(app)
    }

}

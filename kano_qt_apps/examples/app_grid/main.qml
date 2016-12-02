/**
 * launcher.qml
 *
 * Copyright (C) 2016 Kano Computing Ltd.
 * License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
 *
 * Main mode launcher application
 */


import QtQuick 2.3
import QtQuick.Controls 1.4
import QtQuick.Layouts 1.2
import QtQuick.Window 2.2

import Kano.Apps 1.0 as KanoApps


ApplicationWindow {
    id: main_window
    flags: Qt.FramelessWindowHint
    visible: true

    width: 600
    height: 600

    x: (Screen.width - width) / 2
    y: (Screen.height - height) / 2

    KanoApps.AppGrid {
        anchors.fill: parent
    }
}

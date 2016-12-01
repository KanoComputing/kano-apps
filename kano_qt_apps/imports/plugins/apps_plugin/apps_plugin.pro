CONFIG += \
    kano_qml_module \
    link_prl \
    plugin

TARGET = apps_plugin
DESTDIR = ../../Kano/Apps/

SRC_DIR = 'src'
INCLUDE_DIR = $$PWD/includes

INCLUDEPATH += $$INCLUDE_DIR

SOURCES += \
    $$SRC_DIR/apps_plugin.cpp

HEADERS += \
    $$INCLUDE_DIR/apps_plugin.h

include(../../../lib/kano_apps_lib.pri)

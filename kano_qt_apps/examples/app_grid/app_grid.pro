TEMPLATE = app

QMAKE_LFLAGS += -lparson
CONFIG += \
    kano_build_options \
    kano_run_target

RESOURCES += $$PWD/../../fixtures/app_icons.qrc
RESOURCES += $$PWD/app_grid.qrc


SOURCES += \
    src/main.cpp

INCLUDEPATH += $$PWD/includes
HEADERS += \
    includes/core_app.h

include(../../lib/kano_apps_lib.pri)
include(../../imports/imports.pri)

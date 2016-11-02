TEMPLATE = app

QMAKE_LFLAGS += -lparson
CONFIG += \
    kano_build_options \
    kano_run_target
    network

# include(i18n.pri)


SOURCES += \
    src/main.cpp

INCLUDEPATH += $$PWD/includes
HEADERS += \
    includes/core_app.h

include(../lib/kano_apps_lib.pri)

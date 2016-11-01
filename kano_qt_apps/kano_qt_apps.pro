# TODO: Migrate to library ASAP
TEMPLATE = app

QMAKE_LFLAGS += -lparson
CONFIG += \
    kano_build_options \
    network

# include(i18n.pri)


SOURCES += \
    src/main.cpp \
    src/logger.cpp \
    src/app.cpp \
    src/q_app.cpp \
    src/app_list.cpp \
    src/q_app_list.cpp \
    src/download_app_list.cpp

INCLUDEPATH += $$PWD/includes
HEADERS += \
    includes/core_app.h \
    includes/logger.h \
    includes/app.h \
    includes/q_app.h \
    includes/app_list.h \
    includes/q_app_list.h \
    includes/download_app_list.h

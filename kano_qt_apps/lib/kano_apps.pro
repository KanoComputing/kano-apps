TEMPLATE = lib

CONFIG += \
    kano_build_options \
    network

# include(i18n.pri)

SOURCES += \
    src/logger.cpp \
    src/app.cpp \
    src/q_app.cpp \
    src/app_list.cpp \
    src/q_app_list.cpp \
    src/download_app_list.cpp

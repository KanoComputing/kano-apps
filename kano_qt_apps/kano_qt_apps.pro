TEMPLATE = subdirs

SUBDIRS = \
    kano_apps \
    imports

macx {
    SUBDIRS += examples
}

kano_apps.file = lib/kano_apps.pro

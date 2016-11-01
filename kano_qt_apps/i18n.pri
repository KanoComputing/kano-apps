load(kano_i18n)

lupdate_only {
    SOURCES += \
        $$files($$KANO.project_dir/*.qml, true)
}

TRANSLATIONS = \
    $$KANO.i18n_path/kano_qt_apps_es_AR.ts \
    $$KANO.i18n_path/kano_qt_apps_fr_FR.ts

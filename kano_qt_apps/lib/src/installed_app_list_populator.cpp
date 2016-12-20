/**
 * share_list_populator.cpp
 *
 * Copyright (C) 2016 Kano Computing Ltd.
 * License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
 *
 * Populates the Qt share list object (intended to run in a thread)
 */


#include <QDebug>
#include <QFileInfo>
#include <QString>
#include <QThread>
#include <pwd.h>
#include <unistd.h>
#include <parson/parson.h>

#include "installed_app_list_populator.h"
#include "app_list.h"
#include "app.h"
#include "logger.h"


// TODO: Decide if this should be just another `.app` file
const char *APP_STORE_APP = "{ \
    \"type\": \"app\", \
    \"title\": \"App Store\", \
    \"tagline\": \"Go to Kano World to install more\", \
    \"slug\": \"want-more\", \
    \
    \"origin\": \"-\", \
    \
    \"icon\": \"app-store\", \
    \"colour\": \"#fda96f\", \
    \
    \"categories\": [ \
        \"code\", \
        \"media\", \
        \"games\", \
        \"others\", \
        \"tools\", \
        \"experimental\" \
    ], \
    \
    \"packages\": [], \
    \"dependencies\": [\"chromium\"], \
    \"launch_command\": \"kano-world-launcher /apps/\", \
    \"overrides\": [], \
    \"desktop\": false, \
    \"priority\": -10000 \
}";


InstalledAppListPopulator::InstalledAppListPopulator(QDir apps_dir):
    QObject(),
    apps_dir(apps_dir)
{
}


void InstalledAppListPopulator::refresh_list()
{
    QStringList app_files = this->apps_dir.entryList(
        QStringList({"*.app"}), QDir::Files
    );

#ifdef DEBUG
    qDebug() << "Looking in" << this->apps_dir
             << "and found files" << app_files;
#endif  // DEBUG

    QAppList apps;
    QThread *current_thr = QThread::currentThread();

    for (auto app_file : app_files) {
        if (current_thr->isInterruptionRequested()) {
#ifdef DEBUG
            qDebug() << "Apps: Interrupt requested while parsing apps";
#endif  // DEBUG
            return;
        }

        apps.add_app_from_file(this->apps_dir.filePath(app_file).toStdString());
    }

    JSON_Value *app_store_app = json_parse_string(APP_STORE_APP);

    if (app_store_app && json_value_get_type(app_store_app) == JSONObject) {
        JSON_Object *app_store_object = json_value_get_object(app_store_app);

        apps.add_app(
            App(app_store_object)
        );
    } else {
        logger() << "Failed to load App Store JSON";
    }

    if (app_store_app)
        json_value_free(app_store_app);

    // FIXME: Type registration required here despite the Q_DECLARE_METATYPE
    qRegisterMetaType<QAppList>();
    emit this->apps_ready(apps);
}

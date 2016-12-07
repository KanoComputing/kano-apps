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
#include <pwd.h>
#include <unistd.h>
#include <parson/parson.h>

#include "installed_app_list_populator.h"
#include "app_list.h"
#include "app.h"


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
             << " and found files" << app_files;
#endif  // DEBUG

    QAppList apps;

    for (auto app_file : app_files) {
        apps.add_app_from_file(this->apps_dir.filePath(app_file).toStdString());
    }

    // FIXME: Type registration required here despite the Q_DECLARE_METATYPE
    qRegisterMetaType<QAppList>();
    emit this->apps_ready(apps);
}

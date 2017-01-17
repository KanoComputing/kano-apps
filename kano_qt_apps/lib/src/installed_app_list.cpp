/**
 * installed_app_list.cpp
 *
 * Copyright (C) 2016-2017 Kano Computing Ltd.
 * License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
 *
 * Lists the apps intalled on the system
 */


#include <QObject>
#include <parson/parson.h>

#include "app_list.h"
#include "installed_app_list.h"
#include "installed_app_list_populator.h"


InstalledAppList::InstalledAppList():
    QAppList(),
    populate_thr(this)
{
    this->apps_dir.setPath(
        QString::fromStdString(this->config[APPS_DIR_KEY])
    );

    QString locale = QLocale::system().name();
    auto *worker = new InstalledAppListPopulator(this->apps_dir, locale);
    worker->moveToThread(&this->populate_thr);
    connect(
        &this->populate_thr, &QThread::finished,
        worker, &QObject::deleteLater
    );
    connect(
        this, &InstalledAppList::update,
        worker, &InstalledAppListPopulator::refresh_list
    );
    connect(
        worker, &InstalledAppListPopulator::apps_ready,
        this, &InstalledAppList::update_list
    );
    this->populate_thr.start(
        QThread::Priority::LowPriority
    );
}


InstalledAppList::~InstalledAppList()
{
    this->clean_up();
}


void InstalledAppList::update_list(QAppList apps)
{
    this->app_list = apps.app_list;

    emit this->apps_changed();
}

void InstalledAppList::clean_up()
{
    this->populate_thr.requestInterruption();
    this->populate_thr.quit();
    this->populate_thr.wait(100);

    if (this->populate_thr.isRunning()) {
#ifdef DEBUG
        qDebug() << "App List thread still running, forcing it to close";
#endif  // DEBUG
        this->populate_thr.terminate();
        this->populate_thr.wait(100);
    }
}

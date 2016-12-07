#include <QObject>
#include <parson/parson.h>

#include "app_list.h"
#include "installed_app_list.h"
#include "installed_app_list_populator.h"


InstalledAppList::InstalledAppList():
    QAppList()
{
    this->apps_dir.setPath(
        QString::fromStdString(this->config[APPS_DIR_KEY])
    );

    auto *worker = new InstalledAppListPopulator(this->apps_dir);
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
    this->populate_thr.start();
    this->populate_thr.setPriority(QThread::Priority::LowPriority);
}


void InstalledAppList::update_list(QAppList apps)
{
    this->clean_q_app_list();
    this->app_list = apps.app_list;

    emit this->apps_changed();
}

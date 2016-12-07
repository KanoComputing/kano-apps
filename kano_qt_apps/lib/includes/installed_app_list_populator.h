/**
 * installed_app_list_populator.h
 *
 * Copyright (C) 2016 Kano Computing Ltd.
 * License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
 *
 * Populates the Qt installed app list object (intended to run in a thread)
 */


#ifndef __INSTALLED_APP_LIST_POPULATOR_H__
#define __INSTALLED_APP_LIST_POPULATOR_H__


#include <QObject>
#include <QVariant>
#include <QList>
#include <QDir>

#include "app_list.h"
#include "q_app_list.h"


class InstalledAppListPopulator : public QObject
{
    Q_OBJECT

    public:
        InstalledAppListPopulator(QDir apps_dir);

    private:
        const QDir apps_dir;

    public slots:
        void refresh_list();

    signals:
        void apps_ready(QAppList share_list);
};


#endif  // __INSTALLED_APP_LIST_POPULATOR_H__

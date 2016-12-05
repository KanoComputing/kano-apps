#ifndef __INSTALLED_APP_LIST_H__
#define __INSTALLED_APP_LIST_H__


#include <QObject>
#include <QString>
#include <QList>
#include <QtNetwork>
#include <QNetworkAccessManager>
#include <QDir>
#include <QDebug>
#include <QNetworkReply>

#include "app.h"
#include "app_list.h"
#include "q_app_list.h"


class InstalledAppList : public QAppList
{
    Q_OBJECT

    public:
        InstalledAppList();

    protected:
        QDir apps_dir;
        void add_app_from_file(QString file_path);

    private slots:
        void refresh_list();

    signals:
        Q_INVOKABLE void update();
};


#endif  // __INSTALLED_APP_LIST_H__
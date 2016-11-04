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

    public slots:  // Needed?
        void update_app_list(
            unsigned int limit = 10,
            unsigned page = 0,
            QStringList sort_by = {"featured", "likes"}
        );

    protected:
        QDir apps_dir;
        void add_app_from_file(QString file_path);

    private slots:
        void refresh_list(QString res);
};


#endif  // __INSTALLED_APP_LIST_H__

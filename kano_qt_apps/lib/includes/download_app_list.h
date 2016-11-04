#ifndef __DOWNLOAD_APP_LIST_H__
#define __DOWNLOAD_APP_LIST_H__


#include <QObject>
#include <QString>
#include <QList>
#include <QtNetwork>
#include <QNetworkAccessManager>
#include <QUrl>
#include <QDebug>
#include <QNetworkReply>

#include "app.h"
#include "app_list.h"
#include "q_app_list.h"


class DownloadAppList : public QAppList
{
    Q_OBJECT

    public:
        DownloadAppList();

    public slots:  // Needed?
        void update_app_list(
            unsigned int limit = 10,
            unsigned page = 0,
            QStringList sort_by = {"featured", "likes"}
        );

    private:
        QUrl apps_api_endpoint;
        QNetworkAccessManager network_manager;

    private slots:
        void refresh_list(QNetworkReply *reply);
};


#endif  // __DOWNLOAD_APP_LIST_H__

#ifndef __CORE_APP_H__
#define __CORE_APP_H__


#include <QCoreApplication>
#include "download_app_list.h"


class CoreApp : public QCoreApplication
{

    public:
        CoreApp(int argc, char *argv[]):
            QCoreApplication(argc, argv)
            {}
        DownloadAppList apps;
};


#endif  // __CORE_APP_H__

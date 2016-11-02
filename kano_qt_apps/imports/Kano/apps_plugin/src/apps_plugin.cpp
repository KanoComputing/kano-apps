#include <QQmlExtensionPlugin>
#include <QtQml>
#include <QDebug>

#include "apps_plugin.h"
#include "q_app.h"
#include "q_app_list.h"


void AppsPlugin::registerTypes(const char *uri)
{
    // qmlRegisterType<QApp>(uri, 1, 0, "App");
    qmlRegisterType<QAppList>(uri, 1, 0, "AppList");
}

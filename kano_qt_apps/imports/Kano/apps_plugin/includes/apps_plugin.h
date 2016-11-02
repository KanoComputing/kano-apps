#ifndef __APPS_PLUGIN_H__
#define __APPS_PLUGIN_H__


#include <QQmlExtensionPlugin>
#include <QtQml>


class AppsPlugin : public QQmlExtensionPlugin
{
    Q_OBJECT
    Q_PLUGIN_METADATA(IID QQmlExtensionInterface_iid)

    public:
        void registerTypes(const char *uri);
};


#endif  // __APPS_PLUGIN_H__

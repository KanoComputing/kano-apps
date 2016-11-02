#include <QObject>
#include <QNetworkRequest>
#include <QNetworkReply>
#include <parson/parson.h>

#include "installed_app_list.h"


InstalledAppList::InstalledAppList():
    apps_dir("/usr/share/applications")  // TODO: Allow configuration file
{
    this->update_app_list();
}


void InstalledAppList::update_app_list(unsigned int limit, unsigned page,
                                      QStringList sort_by)
{
    qDebug() << "Updating app list";
}


void InstalledAppList::refresh_list(QString res)
{
    qDebug() << "Got response";
    JSON_Value *root = json_parse_string(res.toStdString().c_str());

    if (!root) {
        qDebug() << "Couldn't parse returned JSON";
        return;
    }

    if (json_value_get_type(root) != JSONObject) {
        qDebug() << "Returned JSON isn't a JSON object";
        json_value_free(root);
        return;
    }

    JSON_Object *node = json_value_get_object(root);

    if (!node) {
        qDebug() << "Couldn't get node";
        json_value_free(root);
    }

    JSON_Array *entries = json_object_get_array(node, "entries");
    size_t len = json_array_get_count(entries);

    for (size_t i = 0; i < len; i++) {
        JSON_Object *app_object = json_array_get_object(entries, i);
        this->add_app(App(app_object));
    }

    json_value_free(root);
}

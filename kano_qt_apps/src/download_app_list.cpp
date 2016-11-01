#include <QObject>
#include <QNetworkRequest>
#include <QNetworkReply>
#include <parson/parson.h>

#include "download_app_list.h"


DownloadAppList::DownloadAppList():
    apps_api_endpoint("http://api.kano.me/apps")  // TODO: Allow configuration file
{
    QObject::connect(
        &this->network_manager, SIGNAL(finished(QNetworkReply *)),
        this, SLOT(refresh_list(QNetworkReply *))
    );

    this->update_app_list();
}


void DownloadAppList::update_app_list(unsigned int limit, unsigned page,
                                      QStringList sort_by)
{
    qDebug() << "Updating app list";
    QNetworkRequest req(this->apps_api_endpoint);
    this->network_manager.get(req);
}


void DownloadAppList::refresh_list(QNetworkReply *reply)
{
    qDebug() << "Got response";
    QByteArray res = reply->readAll();

    reply->close();
    reply->deleteLater();


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

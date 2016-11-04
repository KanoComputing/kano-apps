#include <QObject>
#include <QNetworkRequest>
#include <QNetworkReply>
#include <parson/parson.h>

#include "app_list.h"
#include "installed_app_list.h"


InstalledAppList::InstalledAppList():
    QAppList()
{
    this->apps_dir.setPath(
        QString::fromStdString(this->config[APPS_DIR_KEY])
    );
    this->update_app_list();
}


void InstalledAppList::update_app_list(unsigned int limit, unsigned page,
                                      QStringList sort_by)
{
    qDebug() << "Updating local app list";
    this->refresh_list("");  // FIXME
}


void InstalledAppList::add_app_from_file(QString file_path)
{
    JSON_Value *root = json_parse_file(file_path.toStdString().c_str());

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
        return;
    }

    this->add_app(node);

    json_value_free(root);
}


void InstalledAppList::refresh_list(QString res)
{
    qDebug() << "Got response";

    QStringList app_files = apps_dir.entryList(QStringList({"*.app"}), QDir::Files);
    qDebug() << "Found files" << app_files;

    for (auto it = app_files.begin(); it != app_files.end(); ++it) {
        this->add_app_from_file(this->apps_dir.filePath(*it));
    }

    emit this->apps_changed();
}

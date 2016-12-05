#include <QObject>
#include <parson/parson.h>

#include "app_list.h"
#include "installed_app_list.h"


InstalledAppList::InstalledAppList():
    QAppList()
{
    this->apps_dir.setPath(
        QString::fromStdString(this->config[APPS_DIR_KEY])
    );
    this->connect(
        this, SIGNAL(update()),
        this, SLOT(refresh_list())
    );
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


void InstalledAppList::refresh_list()
{

    QStringList app_files = this->apps_dir.entryList(QStringList({"*.app"}), QDir::Files);

#ifdef DEBUG
    qDebug() << "Looking in" << this->apps_dir
             << " and found files" << app_files;
#endif  // DEBUG

    this->clean_q_app_list();

    for (auto app_file : app_files) {
        this->add_app_from_file(this->apps_dir.filePath(app_file));
    }

    emit this->apps_changed();
}

#ifndef __Q_APP_H__
#define __Q_APP_H__


#include <QObject>
#include <QString>
#include <QStringList>
#include <QList>
#include <vector>
#include <parson/parson.h>

#include "app.h"


// TODO: Move me
QString convert_to_qobject(std::string &s);


template <typename QtType, typename Type>
QList<QtType> vec_to_qlist(std::vector<Type> &list)
{
    QList<QtType> q_list;

    for (auto it = list.begin(); it != list.end(); ++it) {
        q_list.push_back(
            convert_to_qobject(*it)
        );
    }

    return q_list;
}

// -----------------------------------------------------------------




class QApp : public QObject, public App
{
    Q_OBJECT
    Q_PROPERTY(QString title
               READ get_title
               CONSTANT)
    Q_PROPERTY(QString tagline
               READ get_tagline
               CONSTANT)
    Q_PROPERTY(QString description
               READ get_description
               CONSTANT)
    Q_PROPERTY(QString slug
               READ get_slug
               CONSTANT)
    Q_PROPERTY(QString icon
               READ get_icon
               CONSTANT)
    Q_PROPERTY(QString color
               READ get_color
               CONSTANT)
    Q_PROPERTY(QStringList categories
               READ get_categories
               CONSTANT)
    Q_PROPERTY(QStringList packages
               READ get_packages
               CONSTANT)
    Q_PROPERTY(QStringList dependencies
               READ get_dependencies
               CONSTANT)
    Q_PROPERTY(QString launch_command
               READ get_launch_command
               CONSTANT)
    Q_PROPERTY(QStringList overrides
               READ get_overrides
               CONSTANT)
    Q_PROPERTY(bool desktop
               READ get_desktop
               CONSTANT)

    public:
        QApp(const QString app_file_path = "");
        QApp(JSON_Object *app_object);
        QApp(const App &other);
        QApp(const QApp &other);
        // QApp& operator=(const App &other);

    protected:
        QString get_title();
        QString get_tagline();
        QString get_description();
        QString get_slug();
        QString get_icon();
        QString get_color();
        QStringList get_categories();
        QStringList get_packages();
        QStringList get_dependencies();
        QString get_launch_command();
        QStringList get_overrides();
        bool get_desktop();
};

Q_DECLARE_METATYPE(QApp)


#endif  // __Q_APP_H__

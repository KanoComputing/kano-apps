/**
 * q_app.h
 *
 * Copyright (C) 2016-2019 Kano Computing Ltd.
 * License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
 *
 * Qt wrapper for the App class to expose the methods to Qt
 */


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
               READ get_q_title
               CONSTANT)
    Q_PROPERTY(QString tagline
               READ get_q_tagline
               CONSTANT)
    Q_PROPERTY(QString description
               READ get_q_description
               CONSTANT)
    Q_PROPERTY(QString slug
               READ get_q_slug
               CONSTANT)
    Q_PROPERTY(QString icon
               READ get_q_icon
               CONSTANT)
    Q_PROPERTY(QString color
               READ get_q_color
               CONSTANT)
    Q_PROPERTY(QStringList categories
               READ get_q_categories
               CONSTANT)
    Q_PROPERTY(QStringList packages
               READ get_q_packages
               CONSTANT)
    Q_PROPERTY(QStringList dependencies
               READ get_q_dependencies
               CONSTANT)
    Q_PROPERTY(QString launch_command
               READ get_q_launch_command
               CONSTANT)
    Q_PROPERTY(QStringList overrides
               READ get_q_overrides
               CONSTANT)
    Q_PROPERTY(bool single_app_mode
               READ get_single_app_mode
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
        QString get_q_title();
        QString get_q_tagline();
        QString get_q_description();
        QString get_q_slug();
        QString get_q_icon();
        QString get_q_color();
        QStringList get_q_categories();
        QStringList get_q_packages();
        QStringList get_q_dependencies();
        QString get_q_launch_command();
        QStringList get_q_overrides();
};

Q_DECLARE_METATYPE(QApp)


#endif  // __Q_APP_H__

/**
 * q_app.cpp
 *
 * Copyright (C) 2016-2017 Kano Computing Ltd.
 * License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
 *
 * Qt wrapper for the App class to expose the methods to Qt
 */


#include <QString>
#include <QStringList>

#include "q_app.h"


// TODO: Move me

QString convert_to_qobject(std::string &s)
{
    return QString::fromStdString(s);
}
// -----------------------------------------------------------------


QApp::QApp(const QString app_file_path):
    QObject(),
    App(app_file_path.toUtf8().constData())
{
}


QApp::QApp(JSON_Object *app_object):
    QObject(),
    App(app_object)
{
}


QApp::QApp(const App &other):
    QObject(),
    App(other)
{
}


QApp::QApp(const QApp &other):
    QObject(),
    App(static_cast<App>(other))
{
}


/*
QApp::QApp& operator=(const App &other)
    QObject(),
    App(other)
{
}
*/




QString QApp::get_q_title()
{
    return QString::fromStdString(this->get_title());
}


QString QApp::get_q_tagline()
{
    return QString::fromStdString(this->get_tagline());
}


QString QApp::get_q_description()
{
    return QString::fromStdString(this->get_description());
}


QString QApp::get_q_slug()
{
    return QString::fromStdString(this->get_slug());
}


QString QApp::get_q_icon()
{
    return QString::fromStdString(this->get_icon());
}


QString QApp::get_q_color()
{
    return QString::fromStdString(this->get_color());
}


QStringList QApp::get_q_categories()
{
    std::vector<std::string> val = this->get_categories();
    return vec_to_qlist<QString, std::string>(val);
}


QStringList QApp::get_q_packages()
{
    std::vector<std::string> val = this->get_packages();
    return vec_to_qlist<QString, std::string>(val);
}


QStringList QApp::get_q_dependencies()
{
    std::vector<std::string> val = this->get_dependencies();
    return vec_to_qlist<QString, std::string>(val);
}


QString QApp::get_q_launch_command()
{
    return QString::fromStdString(this->get_launch_command());
}


QStringList QApp::get_q_overrides()
{
    std::vector<std::string> val = this->get_overrides();
    return vec_to_qlist<QString, std::string>(val);
}

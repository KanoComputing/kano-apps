#include <QString>
#include <QStringList>

#include "q_app.h"


// TODO: Move me

QString convert_to_qobject(std::string &s)
{
    return QString::fromStdString(s);
}
// -----------------------------------------------------------------


QApp::QApp(QString app_file_path):
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


/*
QApp::QApp(const QApp &other):
    QObject(),
    App(other)
{
}
*/


/*
QApp::QApp& operator=(const App &other)
    QObject(),
    App(other)
{
}
*/




QString QApp::get_title()
{
    return QString::fromStdString(this->title);
}


QString QApp::get_tagline()
{
    return QString::fromStdString(this->tagline);
}


QString QApp::get_description()
{
    return QString::fromStdString(this->description);
}


QString QApp::get_slug()
{
    return QString::fromStdString(this->slug);
}


QString QApp::get_icon()
{
    return QString::fromStdString(this->icon);
}


QString QApp::get_color()
{
    return QString::fromStdString(this->color);
}


QStringList QApp::get_categories()
{
    return vec_to_qlist<QString, std::string>(this->categories);
}


QStringList QApp::get_packages()
{
    return vec_to_qlist<QString, std::string>(this->packages);
}


QStringList QApp::get_dependencies()
{
    return vec_to_qlist<QString, std::string>(this->dependencies);
}


QString QApp::get_launch_command()
{
    return QString::fromStdString(this->launch_command);
}


QStringList QApp::get_overrides()
{
    return vec_to_qlist<QString, std::string>(this->overrides);
}


bool QApp::get_desktop()
{
    return this->desktop;
}

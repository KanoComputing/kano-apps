#ifndef __CORE_APP_H__
#define __CORE_APP_H__


#include <QGuiApplication>
#include <QQmlApplicationEngine>


class CoreApp : public QGuiApplication
{

    public:
        CoreApp(int argc, char *argv[]):
            QGuiApplication(argc, argv)
        {
            this->engine.load(
                QUrl(QStringLiteral("qrc:/main.qml"))
            );
        }
        QQmlApplicationEngine engine;
};


#endif  // __CORE_APP_H__

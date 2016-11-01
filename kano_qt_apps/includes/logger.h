#ifndef __LOGGER_H__
#define __LOGGER_H__


#include <QDebug>


#define logger qDebug
class Logger : private QDebug
{
    public:
        Logger(QIODevice *device);
        Logger(QString *string);
        Logger(QtMsgType type);
        Logger(const QDebug &other);
        Logger& operator<<(const std::string &s);
};

// Logger logger();


#endif  // __LOGGER_H__

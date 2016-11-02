#include <QString>

#include "logger.h"


Logger::Logger(QIODevice *device):
    QDebug(device)
{
}


Logger::Logger(QString *string):
    QDebug(string)
{
}


Logger::Logger(QtMsgType type):
    QDebug(type)
{
}


Logger::Logger(const QDebug &other):
    QDebug(other)
{
}


Logger& Logger::operator<<(const std::string &s)
{
    return this->operator<<(s.c_str());
    // QString q_str = QString::fromStdString(s);
    // return this->operator<<(q_str);
    // return this->operator<<(QString::fromUtf8(s.c_str()));
}


/*
Logger logger()
{
    return Logger(qDebug());
}
*/

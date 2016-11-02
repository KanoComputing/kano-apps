#ifndef __Q_APP_LIST_H__
#define __Q_APP_LIST_H__


#include <QObject>
#include <QString>
#include <QList>
#include <QVariant>

#include "app.h"
#include "app_list.h"
#include "q_app.h"


class QAppList : public QObject, public AppList
{
    Q_OBJECT
    Q_PROPERTY(QList<QVariant> app_list
               READ get_app_list)

    public:
        QAppList(QObject *parent = NULL);
        ~QAppList();
        // void add_app(QApp new_app);
        QList<QVariant> get_app_list();

    protected:
        QList<QVariant> q_app_list;
        void clean_q_app_list();
};


#endif  // __Q_APP_LIST_H__

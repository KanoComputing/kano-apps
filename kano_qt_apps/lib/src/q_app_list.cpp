#include "q_app_list.h"


QAppList::QAppList(QObject *parent):
    QObject(parent),
    AppList()
{
}


QAppList::~QAppList()
{
    this->clean_q_app_list();
}


/*
void QAppList::add_app(QApp new_app)
{
    // TODO
    // App *new_app_base = dynamic_cast<App *>(&new_app);
    // this->add_app(static_cast<App>(new_app_base));
    // this->add_app(static_cast<App>(new_app));
}
*/


void QAppList::clean_q_app_list()
{
    /* FIXME
    for (auto it = this->q_app_list.begin(); it != this->q_app_list.end(); ++it) {
        delete(*it);
    }
    */

    while (!this->q_app_list.isEmpty()) {
        auto variant_q_app = this->q_app_list.takeLast();
    }
}


// TODO: Update the array as it changes to avoid calculating this multiple times
QList<QVariant> QAppList::get_app_list()
{
    this->clean_q_app_list();

    QApp *q_app;
    QVariant variant_q_app;

    for (auto it = this->app_list.begin(); it != this->app_list.end(); ++it) {
        q_app = new QApp(*it);
        variant_q_app = QVariant::fromValue(q_app);
        this->q_app_list.push_back(variant_q_app);
    }

    return this->q_app_list;
}

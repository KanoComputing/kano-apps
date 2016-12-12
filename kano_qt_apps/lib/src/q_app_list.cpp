#include "q_app_list.h"


QAppList::QAppList(QObject *parent):
    QObject(parent),
    AppList()
{
}

QAppList::QAppList(const QAppList &other):
    QObject(other.parent()),
    AppList(static_cast<AppList>(other))
{
}

QAppList::QAppList(const AppList &other):
    QObject(nullptr),
    AppList(static_cast<AppList>(other))
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
    while (!this->q_app_list.isEmpty()) {
        QVariant variant_q_app = this->q_app_list.takeLast();
        delete(variant_q_app.value<QApp *>());
    }
}


// TODO: Update the array as it changes to avoid calculating this multiple times
QList<QVariant> QAppList::get_app_list()
{
    this->clean_q_app_list();

    for (auto app : this->app_list) {
        auto q_app = new QApp(app);
        auto variant_q_app = QVariant::fromValue(q_app);
        this->q_app_list.push_back(variant_q_app);
    }

    return this->q_app_list;
}

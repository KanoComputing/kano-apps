/**
 * q_app_list.cpp
 *
 * Copyright (C) 2016-2017 Kano Computing Ltd.
 * License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
 *
 * Qt wrapper for the AppList class to expose the methods to Qt
 */


#include "q_app_list.h"


QAppList::QAppList(QObject *parent):
    QObject(parent),
    QQmlParserStatus(),
    AppList()
{
}

QAppList::QAppList(const QAppList &other):
    QObject(other.parent()),
    QQmlParserStatus(),
    AppList(static_cast<AppList>(other))
{
}

QAppList::QAppList(const AppList &other):
    QObject(nullptr),
    QQmlParserStatus(),
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
QList<QVariant> QAppList::get_app_list(bool filter)
{
    this->clean_q_app_list();

    for (auto app : this->app_list) {
        auto q_app = new QApp(app);

        // If filter is requested and app is hidden, do not add the icon
        if (filter && q_app->get_hidden()) {
            continue;
        }

        auto variant_q_app = QVariant::fromValue(q_app);
        this->q_app_list.push_back(variant_q_app);
    }

    return this->q_app_list;
}


/*
 * Invoked after class creation, but before any properties have been set.
 */
void QAppList::classBegin()
{
}


/**
 * Invoked after the root component that caused this instantiation has
 * completed construction. At this point all static values and binding
 * values have been assigned to the class.
 */
void QAppList::componentComplete()
{
    this->initialise();
}


void QAppList::initialise()
{
}

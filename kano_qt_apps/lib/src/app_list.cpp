/**
 * app_list.cpp
 *
 * Copyright (C) 2016-2018 Kano Computing Ltd.
 * License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
 *
 * Data structure to contain a list of apps
 */


#include <iostream>
#include <unistd.h>
#include <pwd.h>
#include <sys/stat.h>
#include <parson/parson.h>
#include <parson/json_helpers.h>

#include <Kano/TouchDetect/touch_detect.h>

#include "app_list.h"
#include "app.h"
#include "config.h"


AppList::AppList():
    Config(
        {
            {APPS_DIR_KEY, "/usr/share/applications"},
            {API_URL_KEY, "http://api.kano.me/apps"}
        },
        "kano_apps.conf"
    ),
    touch_supported(Kano::TouchDetect::isTouchSupported())
{
}


void AppList::add_app(App new_app, std::shared_ptr<App> fallback)
{
    if (fallback)
        new_app.set_fallback(std::move(fallback));

    int prio = new_app.get_priority();

    for (auto it = this->app_list.begin(); it != this->app_list.end(); ++it) {
        if (it->get_priority() < prio) {
            this->app_list.insert(it, new_app);
            return;
        }
    }

    this->app_list.push_back(new_app);
}


void AppList::add_app(JSON_Object *new_app, std::shared_ptr<App> fallback)
{
    this->add_app(App(new_app, std::move(fallback)));
}


void AppList::add_app_from_file(std::string file_path, std::shared_ptr<App> fallback)
{
    this->add_app(App(file_path), std::move(fallback));
}

void AppList::add_app_from_file(std::string file_path, std::string fallback)
{
    std::shared_ptr<App> fb = nullptr;

    if (!fallback.empty())
        fb = std::make_shared<App>(fallback);

    this->add_app_from_file(file_path, std::move(fb));
}

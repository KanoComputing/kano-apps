#include <iostream>
#include <unistd.h>
#include <pwd.h>
#include <sys/stat.h>
#include <parson/parson.h>
#include <parson/json_helpers.h>

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
    )
{
}


void AppList::add_app(App new_app)
{
    this->app_list.push_back(new_app);
}


void AppList::add_app(JSON_Object *new_app)
{
    this->add_app(App(new_app));
}

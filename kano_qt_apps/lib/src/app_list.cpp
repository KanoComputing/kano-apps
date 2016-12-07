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
    int prio = new_app.get_priority();

    for (auto it = this->app_list.begin(); it != this->app_list.end(); ++it) {
        if (it->get_priority() < prio) {
            this->app_list.insert(it, new_app);
            return;
        }
    }

    this->app_list.push_back(new_app);
}


void AppList::add_app(JSON_Object *new_app)
{
    this->add_app(App(new_app));
}


void AppList::add_app_from_file(std::string file_path)
{
    JSON_Value *root = json_parse_file(file_path.c_str());

    if (!root) {
        std::cout << "Couldn't parse returned JSON";
        return;
    }

    if (json_value_get_type(root) != JSONObject) {
        std::cout << "Returned JSON isn't a JSON object";
        json_value_free(root);
        return;
    }

    JSON_Object *node = json_value_get_object(root);

    if (!node) {
        std::cout << "Couldn't get node";
        json_value_free(root);
        return;
    }

    this->add_app(node);

    json_value_free(root);
}

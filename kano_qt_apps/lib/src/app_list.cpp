#include <iostream>
#include <unistd.h>
#include <pwd.h>
#include <sys/stat.h>
#include <parson/parson.h>
#include <parson/json_helpers.h>

#include "app_list.h"
#include "app.h"


AppList::AppList():
    conf_filename("kano_apps.conf"),
    conf_file_dirs({
        "/etc",
        get_home_dir() + "/.config"
    }),
    config({
        {APPS_DIR_KEY, "/usr/share/applications"},
        {API_URL_KEY, "http://api.kano.me/apps"}
    })

{
    this->load_config();
}

std::string AppList::get_home_dir()
{
    struct passwd *pw = getpwuid(getuid());
    const char *homedir = pw->pw_dir;

    return std::string(homedir);
}

void AppList::load_config()
{
    std::string conf_path;
    for (auto it = this->conf_file_dirs.begin(); it != this->conf_file_dirs.end(); ++it) {
        conf_path = *it + "/" + this->conf_filename;

        std::cout << "Checking file: " << conf_path << "\n";

        if (this->file_exists(conf_path)) {
            std::cout << "Conf file exists: " << conf_path << "\n";
            this->parse_config_file(conf_path);
        }
    }

#ifndef DEBUG  // FIXME
    for (auto it = this->config.begin(); it != this->config.end(); ++it) {
        std::cout << it->first << " : " << it->second << "\n";
    }
#endif  // DEBUG

}


bool AppList::file_exists(const std::string& name) {
    struct stat buffer;
    return (stat(name.c_str(), &buffer) == 0);
}


void AppList::parse_config_file(const std::string& config_file_path)
{
    JSON_Value *root = json_parse_file(config_file_path.c_str());

    if (!root) {
        std::cout << "Couldn't parse returned JSON\n";
        return;
    }

    if (json_value_get_type(root) != JSONObject) {
        std::cout << "Returned JSON isn't a JSON object\n";
        json_value_free(root);
        return;
    }

    JSON_Object *node = json_value_get_object(root);

    if (!node) {
        std::cout << "Couldn't get node\n";
        json_value_free(root);
        return;
    }

    std::string val;

    for (auto it = this->config.begin(); it != this->config.end(); ++it) {
        val = get_json_string(node, it->first);

        if (!val.empty())
            it->second = val;
    }

    json_value_free(root);
}


void AppList::add_app(App new_app)
{
    this->app_list.push_back(new_app);
}


void AppList::add_app(JSON_Object *new_app)
{
    this->add_app(App(new_app));
}

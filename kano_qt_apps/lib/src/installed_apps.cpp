#include <iostream>

#include "installed_apps.h"
#include "app.h"


InstalledApps::InstalledApps():
    Config(
        {
            {APPS_DIR_KEY, "/usr/share/applications"},
        },
        "kano_apps.conf"
    )
{
    this->apps_dir = this->config[APPS_DIR_KEY];
}


App InstalledApps::get_app(const std::string app_name)
{
    std::string app_file_name = app_name + APP_FILE_EXTENSION;

    return App(this->apps_dir + "/" + app_file_name);
}

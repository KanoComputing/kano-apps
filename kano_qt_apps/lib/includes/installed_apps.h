#ifndef __INSTALLED_APPS_H__
#define __INSTALLED_APPS_H__


#include <string>

#include "app.h"
#include "config.h"


const std::string APPS_DIR_KEY = "applications_dir";
const std::string APP_FILE_EXTENSION = ".app";


class InstalledApps : public Config
{
    public:
        InstalledApps();
        App get_app(const std::string app_name);
    protected:
        std::string apps_dir;
};


#endif  // __INSTALLED_APPS_H__

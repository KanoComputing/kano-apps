#ifndef __APP_LIST_H__
#define __APP_LIST_H__


#include <vector>
#include <string>
#include <unordered_map>

#include <parson/parson.h>

#include "app.h"
#include "installed_apps.h"
#include "config.h"


const std::string API_URL_KEY = "api_url";


class AppList : public Config
{

    public:
        AppList();
        void add_app(App new_app);
        void add_app(JSON_Object *new_app);

    protected:
        std::vector<App> app_list;
};


#endif  // __APP_LIST_H__

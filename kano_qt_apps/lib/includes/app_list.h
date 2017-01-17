/**
 * app_list.h
 *
 * Copyright (C) 2016-2017 Kano Computing Ltd.
 * License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
 *
 * Data structure to contain a list of apps
 */


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
        void add_app(App new_app, std::shared_ptr<App> fallback = nullptr);
        void add_app(JSON_Object *new_app, std::shared_ptr<App> fallback = nullptr);
        void add_app_from_file(std::string file_path, std::shared_ptr<App> fallback = nullptr);
        void add_app_from_file(std::string file_path, std::string fallback);

        std::vector<App> app_list;
};


#endif  // __APP_LIST_H__

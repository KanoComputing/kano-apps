#ifndef __APP_LIST_H__
#define __APP_LIST_H__


#include <vector>
#include <string>
#include <unordered_map>

#include <parson/parson.h>

#include "app.h"


#define APPS_DIR_KEY "applications_dir"
#define API_URL_KEY "api_url"


class AppList
{

    public:
        AppList();
        void add_app(App new_app);
        void add_app(JSON_Object *new_app);

    protected:
        static std::string get_home_dir();
        const std::string conf_filename;
        const std::vector<std::string> conf_file_dirs;
        const std::string applications_path;
        std::unordered_map<std::string, std::string> config;

        void load_config();
        inline bool file_exists(const std::string& name);
        void parse_config_file(const std::string& config_file_path);
        std::vector<App> app_list;
};


#endif  // __APP_LIST_H__

#ifndef __CONFIG_H__
#define __CONFIG_H__


#include <vector>
#include <string>
#include <unordered_map>

#include <parson/parson.h>

#include "app.h"


class Config
{

    public:
        Config(
            std::unordered_map<std::string, std::string> default_config,
            std::string config_filename,
            std::vector<std::string> config_dirs = {
                "/etc",
                get_home_dir() + "/.config"
#ifdef DEBUG
                , WORKING_DIR "/../fixtures"
#endif  // DEBUG
            }
        );
        static bool file_exists(const std::string& name);

    protected:
        static std::string get_home_dir();

        void load_config();
        void parse_config_file(const std::string& config_file_path);

        const std::string conf_filename;
        const std::vector<std::string> conf_file_dirs;
        std::unordered_map<std::string, std::string> config;
};


#endif  // __CONFIG_H__

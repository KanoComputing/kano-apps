#include <iostream>
#include <unistd.h>
#include <pwd.h>
#include <sys/stat.h>
#include <parson/parson.h>
#include <parson/json_helpers.h>

#include "config.h"


Config::Config(
    std::unordered_map<std::string, std::string> default_config,
    std::string config_filename,
    std::vector<std::string> config_dirs
) :
    conf_filename(config_filename),
    conf_file_dirs(config_dirs),
    config(default_config)

{
    this->load_config();
}


std::string Config::get_home_dir()
{
    struct passwd *pw = getpwuid(getuid());
    const char *homedir = pw->pw_dir;

    return std::string(homedir);
}


bool Config::file_exists(const std::string& name) {
    struct stat buffer;
    return (stat(name.c_str(), &buffer) == 0);
}


void Config::load_config()
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

#ifdef DEBUG
    std::cout << "\n"
              << "-------------------------------------------------------\n"
              << "Configuration:\n"
              << "-------------------------------------------------------\n";

    for (auto it = this->config.begin(); it != this->config.end(); ++it) {
        std::cout << it->first << " : " << it->second << "\n";
    }

    std::cout << "-------------------------------------------------------\n\n";
#endif  // DEBUG

}


void Config::parse_config_file(const std::string& config_file_path)
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
    bool rel_path;
    const std::string rel_path_pattern = "./";

    for (auto it = this->config.begin(); it != this->config.end(); ++it) {
        val = get_json_val<std::string>(node, it->first);

        if (val.empty())
            continue;

        rel_path = val.find("./") == 0;

        if (rel_path) {
            val = config_file_path.substr(
                    0,
                    config_file_path.length() - this->conf_filename.length()
                ) + val.substr(rel_path_pattern.length());
        }

        it->second = val;
    }

    json_value_free(root);
}

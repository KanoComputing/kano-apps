#ifndef __APP_H__
#define __APP_H__


#include <string>
#include <vector>
#include <parson/parson.h>


class App
{
    public:
        App(std::string app_file_path);
        App(JSON_Object *app_object);
        App(const App &other);
        App& operator=(const App &other);

    protected:
        std::string title;
        std::string tagline;
        std::string description;
        std::string slug;
        std::string icon;
        std::string color;
        std::vector<std::string> categories;
        std::vector<std::string> packages;
        std::vector<std::string> dependencies;
        std::string launch_command;
        std::vector<std::string> overrides;
        bool desktop;
};


#endif  // __APP_H__

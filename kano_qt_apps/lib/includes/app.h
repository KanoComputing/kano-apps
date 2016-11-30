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
        ~App();
        App& operator=(const App &other);

        std::string get_title();
        std::string get_tagline();
        std::string get_description();
        std::string get_slug();
        std::string get_icon();
        std::string get_color();
        std::vector<std::string> get_categories();
        std::vector<std::string> get_packages();
        std::vector<std::string> get_dependencies();
        std::string get_launch_command();
        std::vector<std::string> get_overrides();
        bool get_desktop();
        int get_priority();


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
        int priority;
};


#endif  // __APP_H__

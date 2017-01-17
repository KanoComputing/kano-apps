/**
 * app.h
 *
 * Copyright (C) 2016-2017 Kano Computing Ltd.
 * License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
 *
 * Parses a ".app" file and represents the app described by the file
 */


#ifndef __APP_H__
#define __APP_H__


#include <string>
#include <vector>
#include <parson/parson.h>


class App
{
    public:
        App(std::string app_file_path, std::shared_ptr<App> fallback = nullptr);
        App(JSON_Object *app_object, std::shared_ptr<App> fallback = nullptr);
        App(const App &other, std::shared_ptr<App> fallback = nullptr);
        ~App();
        App& operator=(const App &other);

        bool set_fallback(std::shared_ptr<App> fb);
        std::weak_ptr<App> get_fallback();
        void remove_fallback();

        template<typename T>
        T load_with_fallback(T App:: *member)
        {
            if (this->is_default_param(this->*member) && this->fallback)
                return this->fallback->load_with_fallback(member);

            return this->*member;
        }
        bool is_default_param(const std::string &val);
        bool is_default_param(const std::vector<std::string> &val);
        bool is_default_param(const int &val);

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
        std::shared_ptr<App> fallback;
};


#endif  // __APP_H__

/**
 * app.cpp
 *
 * Copyright (C) 2016-2017 Kano Computing Ltd.
 * License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
 *
 * Parses a ".app" file and represents the app described by the file
 */


#include <string>
#include <vector>
#include <parson/json_helpers.h>

#include "logger.h"
#include "app.h"
#include "config.h"


App::App(std::string app_file_path, std::shared_ptr<App> fb):
    fallback(std::move(fb))
{
    JSON_Value *root = json_parse_file(app_file_path.c_str());

    if (!root) {
        logger() << "Couldn't parse returned JSON";
        return;
    }

    if (json_value_get_type(root) != JSONObject) {
        logger() << "Returned JSON isn't a JSON object";
        json_value_free(root);
        return;
    }

#ifdef DEBUG
    qDebug() << "kano_qt_apps parsing app file: " << app_file_path;
#endif

    JSON_Object *node = json_value_get_object(root);

    this->operator=(
        App(node)
    );

    json_value_free(root);
}


App::App(JSON_Object *app_object, std::shared_ptr<App> fb):
    fallback(std::move(fb))
{
    if (!app_object) {
        logger() << "Attempted to create app from empty object";
        return;
    }

    this->title = get_json_val<std::string>(app_object, "title");
    this->tagline = get_json_val<std::string>(app_object, "tagline");
    this->description = get_json_val<std::string>(app_object, "description");
    this->slug = get_json_val<std::string>(app_object, "slug");
    this->icon = get_json_val<std::string>(app_object, "icon");
    this->hidden = get_json_val<bool>(app_object, "hidden");

    if (this->icon.empty())
        this->icon = get_json_val<std::string>(app_object, "icon_url");

#ifdef DEBUG
    qDebug() << "kano_qt_apps parsed app icon: " << this->icon << " title: '" << this->title << "'";
    if (this->hidden) {
        std::cout << "kano_qt_apps WARNING icon '" << this->icon << "' is set hidden";
    }
#endif

    this->color = get_json_val<std::string>(app_object, "colour");
    this->categories = get_json_array<std::string>(app_object, "categories");
    this->packages = get_json_array<std::string>(app_object, "packages");
    this->dependencies = get_json_array<std::string>(app_object, "dependencies");
    this->launch_command = get_json_val<std::string>(app_object, "launch_command");
    this->overrides = get_json_array<std::string>(app_object, "overrides");
    this->desktop = get_json_val<bool>(app_object, "desktop");
    this->priority = get_json_val<int>(app_object, "priority");

#ifdef DEBUG
    logger() << this->title.c_str() << " - " << this->tagline.c_str();
#endif  // DEBUG
}


App::App(const App &other, std::shared_ptr<App> fb)
{
    this->operator=(other);
    this->set_fallback(std::move(fb));
}


App::~App()
{
    this->remove_fallback();
}


App& App::operator=(const App &other)
{
    this->title = other.title;
    this->tagline = other.tagline;
    this->description = other.description;
    this->slug = other.slug;
    this->icon = other.icon;
    this->color = other.color;
    this->categories = other.categories;
    this->packages = other.packages;
    this->dependencies = other.dependencies;
    this->launch_command = other.launch_command;
    this->overrides = other.overrides;
    this->desktop = other.desktop;
    this->priority = other.priority;
    this->hidden = other.hidden;

    this->fallback = other.fallback;

    return *this;
}


bool App::set_fallback(std::shared_ptr<App> fb)
{
    if (!fb)
        return false;

    if (this->fallback) {
        logger() << "Fallback already set";
        return false;
    }

    this->fallback = std::move(fb);
    return true;
}


std::weak_ptr<App> App::get_fallback()
{
    return this->fallback;
}


void App::remove_fallback() {
    if (this->fallback)
        this->fallback = nullptr;
}


bool App::is_default_param(const std::string &val)
{
    return val.empty();
}


bool App::is_default_param(const std::vector<std::string> &val)
{
    return val.empty();
}


bool App::is_default_param(const int &val)
{
    return val == 0;
}


std::string App::get_title()
{
    return this->load_with_fallback(&App::title);
}


std::string App::get_tagline()
{
    return this->load_with_fallback(&App::tagline);
}


std::string App::get_description()
{
    return this->load_with_fallback(&App::description);
}


std::string App::get_slug()
{
    return this->load_with_fallback(&App::slug);
}


std::string App::get_icon()
{
    std::string icon_name = this->load_with_fallback(&App::icon);

#ifdef DEBUG
    return "qrc:/" + icon_name;
#else  // DEBUG
    const std::vector<std::string> candidate_paths = {
        "/usr/share/icons/Kano/66x66/apps/",
        "/usr/share/icons/Kano/88x88/apps/",
        "/usr/share/icons/hicolor/48x48/apps/",
    };
    const std::vector<std::string> extensions = {
        ".png",
        ".jpeg",
        ".jpg",
    };
    std::string candidate;

    for (auto candidate_path : candidate_paths) {
        for (auto extension : extensions) {
            candidate = candidate_path + icon_name + extension;

            if (Config::file_exists(candidate))
                return candidate;
        }
    }

    return icon_name;
#endif  // DEBUG
}


std::string App::get_color()
{
    return this->load_with_fallback(&App::color);
}


std::vector<std::string> App::get_categories()
{
    return this->load_with_fallback(&App::categories);
}


std::vector<std::string> App::get_packages()
{
    return this->load_with_fallback(&App::packages);
}


std::vector<std::string> App::get_dependencies()
{
    return this->load_with_fallback(&App::dependencies);
}


std::string App::get_launch_command()
{
    return this->load_with_fallback(&App::launch_command);
}


std::vector<std::string> App::get_overrides()
{
    return this->load_with_fallback(&App::overrides);
}


bool App::get_desktop()
{
    // TODO: Without checking explicitly for the existence of the key,
    //       it is very difficult to determine if it is the default
    return this->desktop;
}


int App::get_priority()
{
    return this->load_with_fallback(&App::priority);
}

bool App::get_hidden()
{
    return this->load_with_fallback(&App::hidden);
}

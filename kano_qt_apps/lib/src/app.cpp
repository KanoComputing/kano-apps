#include <string>
#include <vector>
#include <parson/json_helpers.h>

#include "logger.h"
#include "app.h"
#include "config.h"


App::App(std::string app_file_path)
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

    JSON_Object *node = json_value_get_object(root);

    this->operator=(
        App(node)
    );

    json_value_free(root);
}


App::App(JSON_Object *app_object)
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

    if (this->icon.empty())
        this->icon = get_json_val<std::string>(app_object, "icon_url");

    this->color = get_json_val<std::string>(app_object, "colour");
    this->categories = get_json_array<std::string>(app_object, "categories");
    this->packages = get_json_array<std::string>(app_object, "packages");
    this->dependencies = get_json_array<std::string>(app_object, "dependencies");
    this->launch_command = get_json_val<std::string>(app_object, "launch_command");
    this->overrides = get_json_array<std::string>(app_object, "overrides");
    this->desktop = get_json_val<bool>(app_object, "desktop");
    this->priority = get_json_val<int>(app_object, "priority");

    logger() << this->title.c_str() << " - " << this->tagline.c_str();
}


App::App(const App &other)
{
    this->operator=(other);
}


App::~App()
{
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

    return *this;
}


std::string App::get_title()
{
    return this->title;
}


std::string App::get_tagline()
{
    return this->tagline;
}


std::string App::get_description()
{
    return this->description;
}


std::string App::get_slug()
{
    return this->slug;
}


std::string App::get_icon()
{
#ifdef DEBUG
    return "qrc:/" + this->icon;
#else  // DEBUG
    const std::vector<std::string> candidate_paths = {
        "/usr/share/icons/Kano/66x66/apps/",
        "/usr/share/icons/hicolor/48x48/apps/",
    };

    for (auto candidate : candidate_paths) {
        candidate += this->icon + ".png";

        if (Config::file_exists(candidate))
            return candidate;
    }

    return this->icon;
#endif  // DEBUG
}


std::string App::get_color()
{
    return this->color;
}


std::vector<std::string> App::get_categories()
{
    return this->categories;
}


std::vector<std::string> App::get_packages()
{
    return this->packages;
}


std::vector<std::string> App::get_dependencies()
{
    return this->dependencies;
}


std::string App::get_launch_command()
{
    return this->launch_command;
}


std::vector<std::string> App::get_overrides()
{
    return this->overrides;
}


bool App::get_desktop()
{
    return this->desktop;
}


int App::get_priority()
{
    return this->priority;
}

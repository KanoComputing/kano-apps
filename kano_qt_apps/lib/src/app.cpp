#include <string>
#include <parson/json_helpers.h>

#include "logger.h"
#include "app.h"


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

    this->title = get_json_string(app_object, "title");
    this->tagline = get_json_string(app_object, "tagline");
    this->description = get_json_string(app_object, "description");
    this->slug = get_json_string(app_object, "slug");
    this->icon = get_json_string(app_object, "icon");
    this->color = get_json_string(app_object, "colour");
    // this->categories = json_object_get_string(app_object, "categories");
    // this->packages = json_object_get_string(app_object, "packages");
    // this->dependencies = json_object_get_string(app_object, "dependencies");
    // this->launch_command = json_object_get_string(app_object, "launch_command");
    // this->overrides = json_object_get_string(app_object, "overrides");
    // this->desktop = json_object_get_string(app_object, "desktop");

    logger() << this->title.c_str() << " - " << this->tagline.c_str();
}


App::App(const App &other)
{
    this->operator=(other);
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

    return *this;
}

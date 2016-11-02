#include "app_list.h"


AppList::AppList()
{
}


void AppList::add_app(App new_app)
{
    this->app_list.push_back(new_app);
}

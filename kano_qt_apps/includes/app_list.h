#ifndef __APP_LIST_H__
#define __APP_LIST_H__


#include <vector>
#include <string>

#include "app.h"


class AppList
{

    public:
        AppList();
        void add_app(App new_app);

    protected:
        const std::string applications_path;
        std::vector<App> app_list;
};


#endif  // __APP_LIST_H__

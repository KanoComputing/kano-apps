#include <iostream>

#include "core_app.h"

#include "app.h"
#include "app_list.h"
#include "download_app_list.h"
#include "installed_apps.h"


int main(int argc, char *argv[])
{
    InstalledApps installed;
    App pong = installed.get_app("make-pong");
    std::cout << "Pong name: " << pong.get_title() << "\n";
    std::cout << "Pong tagline: " << pong.get_tagline() << "\n";

    CoreApp application(argc, argv);
    application.exec();

    return 0;
}

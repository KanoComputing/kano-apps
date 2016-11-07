#include "core_app.h"

#include "app.h"
#include "app_list.h"
#include "download_app_list.h"


int main(int argc, char *argv[])
{
    CoreApp application(argc, argv);
    application.exec();

    return 0;
}

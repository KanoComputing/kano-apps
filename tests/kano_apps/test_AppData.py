# -*- coding: utf-8 -*-
import json
import os
from mock import patch

from kano_apps.AppData import get_applications

TEST_APP = {
    "title": "Test App",
    "tagline": "Test application",
    "description": "This is a test application to, well, test things.",
    "slug": "test-app",

    "icon": "test",
    "colour": "#F4A15D",

    "categories": ["code"],

    "overrides": ["blacklisted.app"],

    "packages": [],
    "dependencies": [],
    "launch_command": "echo 'Hi''"
}

# Blame Google translate...
TEST_APP_ES = {
    "title": "Pruebas",
    "tagline": u"Aplicación de prueba",
    "description": u"Esta es una aplicación de prueba para, así, las cosas de la prueba.",
    "slug": "test-app",

    "icon": "test",
    "colour": "#F4A15D",

    "categories": ["code"],

    "packages": [],
    "dependencies": [],
    "launch_command": "echo 'Hola''"
}


def test_get_applications(tmpdir):
    application_dir = tmpdir.mkdir('applications')

    # create some fake applications
    test_app_1 = application_dir.join('test-app-1.app')
    test_app_1.write(json.dumps(TEST_APP))

    with patch(
        'kano_apps.AppData._SYSTEM_APPLICATIONS_LOC',
        os.path.join(application_dir.strpath, '')
    ):
        apps = get_applications()

    assert len(apps) == 1

    test_app = apps[0]
    assert test_app['title'] == 'Test App'
    assert test_app['launch_command'] == {
        'cmd': 'echo',
        'args': ['Hi'],
    }


@patch('kano_apps.AppData.locale.getlocale')
def test_get_applications_locale(mock_getlocale, tmpdir):
    mock_getlocale.return_value = ('es_AR', '')

    application_dir = tmpdir.mkdir('applications')

    # create some fake applications
    test_app_1 = application_dir.join('test-app-1.app')
    test_app_1.write(json.dumps(TEST_APP))

    test_app_1_es = application_dir.join('locale', 'es_AR', 'test-app-1.app')
    test_app_1_es.write(json.dumps(TEST_APP_ES), ensure=True)

    with patch(
        'kano_apps.AppData._SYSTEM_APPLICATIONS_LOC',
        os.path.join(application_dir.strpath, '')
    ):
        apps = get_applications()

    assert len(apps) == 1

    test_app = apps[0]
    assert test_app['title'] == 'Pruebas'
    assert test_app['launch_command'] == {
        'cmd': 'echo',
        'args': ['Hola'],
    }


def test_get_applications_blacklist(tmpdir):
    application_dir = tmpdir.mkdir('applications')

    # create some fake applications
    test_app_1 = application_dir.join('test-app-1.app')
    test_app_1.write(json.dumps(TEST_APP))

    blacklisted_app = application_dir.join('blacklisted.app')
    blacklisted_app.write(json.dumps(TEST_APP))

    with patch(
        'kano_apps.AppData._SYSTEM_APPLICATIONS_LOC',
        os.path.join(application_dir.strpath, '')
    ):
        apps = get_applications()

    assert len(apps) == 1

    test_app = apps[0]
    assert test_app['title'] == 'Test App'

# -*- coding: utf-8 -*-
import json
import pytest
from mock import patch

from kano_apps.AppManage import download_app, AppDownloadError
from kano_i18n.init import install


@patch('kano_apps.AppManage.query_for_app')
@patch('kano_apps.AppManage.download_url')
@patch('kano_apps.AppManage.has_min_performance')
def test_download_app_error(
     mock_has_min_performance, mock_download_url, mock_query_for_app
):
    mock_query_for_app.return_value = json.loads(
        '{ "icon_url": "foo.bar", "min_performance_score": 1, "title": "¡Hola!" }'
    )
    mock_has_min_performance.return_value = True
    mock_download_url.return_value = (True, None)

    install('kano-apps')

    with pytest.raises(AppDownloadError) as excinfo:
        download_app('foo')
    assert u'¡Hola!' in _(unicode(excinfo))

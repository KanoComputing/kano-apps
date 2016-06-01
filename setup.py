#!/usr/bin/env python

from distutils.core import setup
import setuptools
import os

def get_locales():
    locale_dir = 'locale'
    locales = []

    for dirpath, dirnames, filenames in os.walk(locale_dir):
        for filename in filenames:
            locales.append(
                (os.path.join('/usr/share', dirpath),
                 [os.path.join(dirpath, filename)])
            )

    return locales


setup(name='Kano Apps',
      version='1.0',
      description='A simple app to launch various program',
      author='Team Kano',
      author_email='dev@kano.me',
      url='https://github.com/KanoComputing/kano-apps',
      packages=['kano_apps', 'kano_world.hook'],
      package_dir={'kano_apps': 'kano_apps', 'kano_world.hook': 'kano-world-hook'},
      package_data={'kano_apps': ['media/*']},
      scripts=['bin/kano-apps', 'bin/update-app-dir'],
      data_files=[
          ('/usr/share/applications', setuptools.findall('apps')), # *.app
          ('/usr/share/icons/Kano/66x66/apps', setuptools.findall('apps/icons')),
          ('/usr/share/kano-apps', setuptools.findall('books')),
          ('/usr/share/kano-desktop/kdesk/kdesktop', ['kdesk-icon/Apps.lnk']),
          ('/usr/share/kano-desktop/icons', setuptools.findall('kdesk-icon')) # *.png
      ] + get_locales()
     )


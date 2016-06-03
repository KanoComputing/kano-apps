#!/usr/bin/env python

from distutils.core import setup
import setuptools
import os
import sys

if '--install-scripts' not in sys.argv:
    sys.argv.push('--install-scripts=/usr/bin')

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

def get_files_in_dir(dir_name, suffix=None):
    files = []

    for dirpath, dirnames, filenames in os.walk(dir_name):
        for filename in filenames:
            if suffix is None or filename.endswith(suffix):
                files.append(filename)

    return files


setup(name='Kano Apps',
      version='1.0',
      description='A simple app to launch various program',
      author='Team Kano',
      author_email='dev@kano.me',
      url='https://github.com/KanoComputing/kano-apps',
      packages=['kano_apps'],
      package_data={'kano_apps': ['media/*']},
      scripts=['bin/kano-apps', 'bin/update-app-dir'],
      data_files=[
          ('/usr/share/applications', get_files_in_dir('apps', '.app')),
          ('/usr/share/icons/Kano/66x66/apps', setuptools.findall('apps/icons')),
          ('/usr/share/kano-apps', setuptools.findall('books')),
          ('/usr/share/kano-desktop/kdesk/kdesktop', ['kdesk-icon/Apps.lnk']),
          ('/usr/share/kano-desktop/icons', get_files_in_dir('kdesk-icon', '.png')),
          ('/usr/lib/python2.7/dist-packages/kano_world/hooks', setuptools.findall('kano-world-hook/'))
      ] + get_locales()
     )


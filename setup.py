#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Note: To use the 'upload' functionality of this file, you must install Twine:
#   $ pip install -r requirements.txt

import io
import os
import sys
from shutil import rmtree

from setuptools import find_packages, setup, Command

# Package meta-data.
NAME = 'inventory'
DESCRIPTION = 'An inventory management CLI'
URL = 'https://github.com/mirrorkeydev/inventory'
EMAIL = 'mirrorkeydev@gmail.com'
AUTHOR = 'Melanie Gutzmann'
REQUIRES_PYTHON = '>=3.9.0'
VERSION = None
LICENSE = 'MIT'
# What packages are required for this module to be executed?
REQUIRED = [
  'google-api-python-client',
  'google-auth-httplib2',
  'google-auth-oauthlib'
]

setup(
  name=NAME,
  description=DESCRIPTION,
  author=AUTHOR,
  author_email=EMAIL,
  python_requires=REQUIRES_PYTHON,
  url=URL,
  # py_modules=['mypackage'],

  entry_points={
    'console_scripts': ['inventory=inventory.cli:main'],
  },
  install_requires=REQUIRED,
  include_package_data=True,
  license=LICENSE,
  classifiers=[
    # Trove classifiers
    # Full list: https://pypi.python.org/pypi?%3Aaction=list_classifiers
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.9',
    'Programming Language :: Python :: Implementation :: CPython',
    'Programming Language :: Python :: Implementation :: PyPy'
  ],
)

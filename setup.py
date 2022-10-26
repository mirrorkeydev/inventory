#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup

# Package metadata.
NAME = 'inventory'
DESCRIPTION = 'An inventory management CLI'
URL = 'https://github.com/mirrorkeydev/inventory'
EMAIL = 'mirrorkeydev@gmail.com'
AUTHOR = 'Melanie Gutzmann'
REQUIRES_PYTHON = '>=3.9.0'
VERSION = None
LICENSE = 'Apache-2.0'
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

  entry_points={
    'console_scripts': ['inventory=inventory.cli:main'],
  },
  install_requires=REQUIRED,
  include_package_data=True,
  license=LICENSE,
  packages=["inventory"],
  classifiers=[
    # Trove classifiers
    # Full list: https://pypi.python.org/pypi?%3Aaction=list_classifiers
    'Programming Language :: Python',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.9',
  ],
)

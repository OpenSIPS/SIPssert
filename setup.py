#!/usr/bin/env python
##
## This file is part of SIPssert
## (see https://github.com/OpenSIPS/SIPssert).
##
## This program is free software: you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation, either version 3 of the License, or
## (at your option) any later version.
##
## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with this program. If not, see <http://www.gnu.org/licenses/>.
##

"""
Installs SIPssert framework tool
"""

import os

try:
    from setuptools import setup, Command
except ImportError:
    from distutils.core import setup, Command

from sipssert import info


here = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(here, 'README.md'), encoding='utf-8') as fh:
    long_description = fh.read()

class CleanCommand(Command):
    user_options = [
            ('all', None, '(Compatibility with original clean command)')
    ]
    def initialize_options(self):
        self.all = False
    def finalize_options(self):
        pass
    def run(self):
        os.system('rm -vrf ./build ./dist ./*.pyc ./*.tgz ./*.egg-info')

setup(
    name = info.__name__,
    version = info.__version__,
    author = "OpenSIPS Project",
    author_email = "project@opensips.org",
    maintainer = "Razvan Crainea",
    maintainer_email = "razvan@opensips.org",
    description = info.__description__,
    long_description = long_description,
    long_description_content_type='text/markdown',
    packages = [
        "sipssert",
        "sipssert.tasks",
        "sipssert.network",
    ],
    install_requires=[
        'docker',
        'jinja2',
        'pyjwt',
        'pyaml',
        'junit-xml',
    ],
    classifiers = [
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
    entry_points = {
        "console_scripts": ["sipssert=sipssert.main:main"],
    },
    cmdclass={
        'clean': CleanCommand,
    }
)

# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

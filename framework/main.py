#!/usr/bin/env python
##
## TODO: update project's name
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

import os
import argparse
from framework import controller

arg_parser = argparse.ArgumentParser(description='Testing Framework for OpenSips Solutions')

arg_parser.add_argument('tests',
                        help='Absolute path of the tests director',
                        type=os.path.abspath,
                        nargs='+')

arg_parser.add_argument('--config',
                        help='Absolute path of the global config',
                        type=os.path.abspath)

# TODO: add a config path


def main():

    # Parse all arguments
    args = arg_parser.parse_args()

    # Open the Controller
    ctrl = controller.Controller(args.tests, args.config)
    ctrl.run()

if __name__ == '__main__':
    main()

# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

#!/usr/bin/env python
##
## This file is part of the SIPssert Testing Framework project
## Copyright (C) 2023 OpenSIPS Solutions
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
import sys
import argparse
from sipssert import controller
from sipssert import info

arg_parser = argparse.ArgumentParser(description=info.__description__)

arg_parser.add_argument('tests',
                        help='Absolute path of the tests director',
                        type=os.path.abspath,
                        nargs='*')

arg_parser.add_argument('-t', '--test',
                        help='Pattern that specify the tests to run. ' \
                                'Can be specified multiple times. ' \
                                'Default value = run all tests',
                        action='append',
                        metavar='[SET/]TEST',
                        default=[])

arg_parser.add_argument('-e', '--exclude',
                        help='Pattern that specify the tests to exclude. ' \
                                'Can be specified multiple times. ' \
                                'Default value = do not exclude any test',
                        action='append',
                        metavar='[SET/]TEST',
                        default=[])

arg_parser.add_argument('-E', '--extra-var',
                        help='Set additional variable as key=value. ' \
                                'Can be specified multiple times',
                        action='append',
                        default=[])

arg_parser.add_argument('-c', '--config',
                        help='Absolute path of the running config',
                        default="run.yml",
                        type=os.path.abspath)

arg_parser.add_argument('-x', '--no-trace',
                        help='Do not trace call',
                        default=False,
                        action='store_true')

arg_parser.add_argument('-l', '--logs-dir',
                        help='Absolute path of the logs dir',
                        default="logs/",
                        type=os.path.abspath)

arg_parser.add_argument('-n', '--no-delete',
                        help='Do not delete resources after run',
                        default=False,
                        action='store_true')

arg_parser.add_argument('-j', '--junit-xml',
                        help='Generate junit compatible report',
                        default=False,
                        action='store_true')

arg_parser.add_argument('-v', '--version',
                        action='version',
                        help='Returns the version of the tool',
                        version=f'%(prog)s {info.__version__}')


def main():
    """Framework entrypoint"""

    # Parse all arguments
    args = arg_parser.parse_args()

    # Open the Controller
    ctrl = controller.Controller(args)
    ctrl.run()
    if ctrl.failed:
        sys.exit(-1)

if __name__ == '__main__':
    main()

# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

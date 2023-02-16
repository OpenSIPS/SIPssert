#!/usr/bin/env python
##
## This file is part of the SIPssert Testing Framework project
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
from sipssert import controller

arg_parser = argparse.ArgumentParser(description='SIPssert Testing Framework')

arg_parser.add_argument('tests',
                        help='Absolute path of the tests director',
                        type=os.path.abspath,
                        nargs='+')

arg_parser.add_argument('-t', '--test',
                        help='Run only specific tests. ' \
                                'Can be specified multiple times. ' \
                                'Default value = run all tests',
                        action='append',
                        default=[])

arg_parser.add_argument('-c', '--config',
                        help='Absolute path of the global config',
                        default="config.yml",
                        type=os.path.abspath)

arg_parser.add_argument('-l', '--logs-dir',
                        help='Absolute path of the logs dir',
                        default="logs/",
                        type=os.path.abspath)

def main():
    """Framework entrypoint"""

    # Parse all arguments
    args = arg_parser.parse_args()

    # Open the Controller
    ctrl = controller.Controller(args)
    ctrl.run()

if __name__ == '__main__':
    main()

# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

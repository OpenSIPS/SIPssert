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

"""Implements the controller's logic"""

import os
import docker
from datetime import datetime
from framework import tests_set
from framework import config
from framework import logger
from framework import testing


class Controller:

    """Controller class that implements the logic"""

    def __init__(self, args):
        self.sets_dirs = args.tests
        self.tests = args.test
        self.logs_dir = args.logs_dir
        self.config_file = args.config
        current_date = datetime.now().strftime("%Y-%m-%d.%H:%M:%S.%f")
        self.run_logs_dir = os.path.join(self.logs_dir, current_date)
        self.link_file = os.path.join(self.logs_dir, "latest")
        self.create_run_logs_dir()
        self.config = config.Config(self.config_file)
        logger.init_logger(self.config["logging"]["controller"], self.run_logs_dir)
        self.docker = docker.from_env()
        self.tlogger = testing.Testing("Running Testing framework")
    
    def create_run_logs_dir(self):
        """Creates the current run logs directory"""
        if not os.path.isdir(self.logs_dir):
            os.mkdir(self.logs_dir)
        if not os.path.isdir(self.run_logs_dir):
            os.mkdir(self.run_logs_dir)
        if os.path.exists(self.link_file):
            os.remove(self.link_file)
        os.symlink(self.run_logs_dir, self.link_file)

    def run(self):
        """Runs all test sets"""
        for test_set in self.sets_dirs:
            test_set_obj = tests_set.TestsSet(test_set, self, self.tests)
            self.tlogger.test_set(f"Running test set: {test_set_obj.name}")
            test_set_obj.run()
        self.tlogger.end()

# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

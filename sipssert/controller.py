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

"""Implements the controller's logic"""

import os
import docker
from datetime import datetime
from sipssert import tests_set
from sipssert import config
from sipssert import logger
from sipssert import testing
from sipssert import tests_filters
from sipssert import junit_reporter


class Controller:

    """Controller class that implements the logic"""

    def __init__(self, args):
        # parse extra vars
        extra_var_dict = {}
        for var in args.extra_var:
            k, v = var.split('=')
            extra_var_dict[k] = v
        self.config_file = args.config
        try:
            self.config = config.Config(self.config_file, None, "defines.yml", template_vars=extra_var_dict)
        except config.ConfigParseError:
            raise Exception(f"could not parse {self.config_file}")
        if len(args.tests):
            self.sets_dirs = args.tests
        else:
            self.sets_dirs = list(map(os.path.abspath,
                                      self.config.get("tests", [])))
        test_filters = args.test if len(args.test) else \
                self.config.get("test", [])
        exclude_filters = args.exclude if len(args.exclude) else \
                self.config.get("exclude", [])
        self.filters = (tests_filters.ParseTestsFilters(test_filters),
                        tests_filters.ParseTestsFilters(exclude_filters))
        self.logs_dir = args.logs_dir
        self.no_delete = args.no_delete
        self.junit_xml = self.config.get("junit", False) \
                if not args.junit_xml else args.junit_xml
        self.no_trace = not self.config.get("tracer", True) \
                if not args.no_trace else args.no_trace
        current_date = datetime.now().strftime("%Y-%m-%d.%H:%M:%S.%f")
        self.run_logs_dir = os.path.join(self.logs_dir, current_date)
        self.link_file = os.path.join(self.logs_dir, "latest")
        self.create_run_logs_dir()
        if self.config.get("logging"):
            logging = self.config.get("logging").get("controller")
        else:
            logging = None

        logger.init_logger(logging, self.run_logs_dir)
        self.docker = docker.from_env()
        self.tlogger = testing.Testing("Running SIPssert Testing Framework")
        self.failed = True

        if self.junit_xml:
            self.junit_reporter = junit_reporter.JUnitReporter("controller")
    
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
            if not os.path.isdir(test_set):
                continue
            test_set_obj = tests_set.TestsSet(test_set, self, self.filters)
            self.tlogger.test_set(f"Running test set: {test_set_obj.name}")
            test_set_obj.run()
        self.failed = self.tlogger.end()
        if self.junit_xml:
            self.junit_reporter.save_report(os.path.join(self.run_logs_dir, "report.xml"))

# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

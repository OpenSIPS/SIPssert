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

import docker
from datetime import datetime
from framework import tests_set
from framework import parser
from framework import controllerLogger
class Controller:

    def __init__(self, sets_dirs, global_config):
        self.sets_dirs = sets_dirs
        p = parser.Parser()
        self.global_config = p.parse_yaml(global_config)
        controllerLogger.initLogger(self.global_config["logging"]["controller"])
        self.docker = docker.from_env()

    def __del__(self):
        pass

    def run(self):
        controllerLogger.clog.warning("Running Tests!")
        for set in self.sets_dirs:
            s = tests_set.TestSet(set, self)
            controllerLogger.clog.info("Start test: {}".format(set))
            s.run()

# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

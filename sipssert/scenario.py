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

"""Scenario running functions"""

import os
import importlib
import time
from datetime import datetime
from sipssert import task
from sipssert import logger
from sipssert import config
from sipssert import tracer
from sipssert import tasks_list

LOGS_DIR = "logs"
NETWORK_CAP = "net_capture"
VARIABLES = "defines.yml"

class Scenario():

    """Class that implements running a scenario"""

    def __init__(self, scenario_file, controller, test_set, set_logs_dir, set_defaults_dict):
        self.controller = controller
        self.tlogger = controller.tlogger
        self.dirname = os.path.dirname(scenario_file)
        self.scenario = os.path.basename(scenario_file)
        self.name = os.path.basename(self.dirname)
        self.scen_logs_dir = os.path.join(set_logs_dir, self.name)
        try:
            self.config = config.Config(self.dirname, self.scenario, VARIABLES,
                    test_set.config.get_defines())
        except config.ConfigParseError:
            raise Exception("could not parse {}".format(self.scenario))
        self.create_scen_logs_dir()
        self.network = self.config.get("network", test_set.default_network)
        self.networks = self.config.get("networks", test_set.default_networks)
        nets = self.networks if self.networks else []
        if self.network:
            nets.append(self.network)
        self.no_trace = self.controller.no_trace
        if not self.no_trace:
            self.tracer = tracer.Tracer(self.scen_logs_dir, "capture", nets, self.name)
        self.timeout = self.config.get("timeout", 0)
        container_prefix = f"{test_set.name}/{self.name}"
        self.tasks = tasks_list.TasksList("tasks", self.dirname, self.scen_logs_dir,
                self.config, self.controller, self.network, self.networks,
                container_prefix, set_defaults_dict)
        self.init_tasks = tasks_list.TasksList("init_tasks", self.dirname, self.scen_logs_dir,
                self.config, self.controller, self.network, self.networks,
                container_prefix, set_defaults_dict)
        self.cleanup_tasks = tasks_list.TasksList("cleanup_tasks", self.dirname, self.scen_logs_dir,
                self.config, self.controller, self.network, self.networks,
                container_prefix, set_defaults_dict)
        if self.timeout != 0:
            self.init_tasks.set_timeout(self.timeout)
            self.tasks.set_timeout(self.timeout)
            self.cleanup_tasks.set_timeout(self.timeout)

    def create_scen_logs_dir(self):
        """Creates current scenario logs directory"""
        if not os.path.isdir(self.scen_logs_dir):
            os.mkdir(self.scen_logs_dir)

    def run(self):
        """Runs a scenario with all its prerequisits"""
        start_time = time.time()
        self.tlogger.test_start(self.name)
        if not self.no_trace:
            self.tracer.start()
        try:
            self.init_tasks.run()
            try:
                self.tasks.run()
            except Exception:
                logger.slog.exception("Error occured during tasks run")
        except Exception:
            logger.slog.exception("Error occured during init tasks")
        try:
            self.cleanup_tasks.run(force_all=True)
        except Exception:
            logger.slog.exception("Error occured during cleanup task")
        if not self.no_trace:
            self.tracer.stop()
        logger.slog.debug("scenario executed in {:.3f}s".format(time.time() - start_time))
        self.tlogger.status(self.tasks.status)

    def __del__(self):
        pass

# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

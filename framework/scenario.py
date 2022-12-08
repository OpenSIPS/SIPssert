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

"""Scenario running functions"""

import os
import importlib
import time
from datetime import datetime
from framework.tasks import task
from framework import logger
from framework import config
from framework import tracer
from framework import tasks_list

LOGS_DIR = "logs"
NETWORK_CAP = "net_capture"
VARIABLES = "defines.yml"

class Scenario():

    """Class that implements running a scenario"""

    def __init__(self, file, controller, test_set, set_logs_dir, set_defaults_dict):
        self.controller = controller
        self.file = file
        self.tlogger = controller.tlogger
        self.dirname = os.path.dirname(file)
        self.scenario = os.path.basename(file)
        self.name = os.path.basename(self.dirname)
        self.scen_logs_dir = set_logs_dir + "/" + self.name
        self.config = config.Config(self.dirname, self.scenario, VARIABLES,
                test_set.config.get_defines())
        self.create_scen_logs_dir()
        self.network_device = self.config.get("network")
        self.tracer = tracer.Tracer(self.scen_logs_dir, "capture", self.network_device)
        self.timeout = self.config.get("timeout", 0)
        self.tasks = tasks_list.TasksList("tasks", self.file, self.scen_logs_dir,
                self.config, self.controller, set_defaults_dict)
        self.init_tasks = tasks_list.TasksList("init_tasks", self.file, self.scen_logs_dir,
                self.config, self.controller, set_defaults_dict)
        self.cleanup_tasks = tasks_list.TasksList("cleanup_tasks", self.file, self.scen_logs_dir,
                self.config, self.controller, set_defaults_dict)
        if self.timeout != 0:
            self.init_tasks.set_timeout(self.timeout)
            self.tasks.set_timeout(self.timeout)
            self.cleanup_tasks.set_timeout(self.timeout)

    def create_scen_logs_dir(self):
        """Creates current scenario logs directory"""
        if not os.path.isdir(self.scen_logs_dir):
            os.mkdir(self.scen_logs_dir)

    def init(self):
        """Runs the init tasks for a scenario"""
        for task in self.init_tasks:
            task.run()

    def cleanup(self):
        """Runs the cleanup tasks for a scenario"""
        for task in self.cleanup_tasks:
            task.run()

    def run(self):
        """Runs a scenario with all its prerequisits"""
        self.tlogger.test_start(self.name)
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
        self.tracer.stop()
        self.verify_test()

    def update(self):
        """updates the status of a scenario"""
        for tsk in self.tasks:
            tsk.update()

    def verify_test(self):
        ok = True
        for task in self.tasks:
            if task.get_exit_code() != 0 and task.daemon == False:
                ok = False
                break
        if ok == False:
            logger.slog.info("Test: {} FAIL!".format(self.name))
            self.tlogger.failed()
        else:
            logger.slog.info("Test: {} PASS!".format(self.name))
            self.tlogger.success()

    def __del__(self):
        pass

# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

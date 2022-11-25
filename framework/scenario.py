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
import subprocess
from framework.tasks import task
from framework import logger
from framework import config
from framework import parser

LOGS_DIR = "logs"
NETWORK_CAP = "net_capture"
VARIABLES = "defines.yml"

class Scenario():

    """Class that implements running a scenario"""

    def __init__(self, file, controller, set_logs_dir, set_vars_dict, set_defaults_dict):
        self.tcpdump = None
        self.controller = controller
        self.file = file
        self.tlogger = controller.tlogger
        self.dirname = os.path.dirname(file)
        self.name = os.path.basename(self.dirname)
        self.scen_logs_dir = set_logs_dir + "/" + self.name
        self.fetch_vars()
        if set_vars_dict:
            self.variables = set_vars_dict | self.variables
        self.config = config.FrameworkConfig(file, False, self.variables)
        self.tasks = []
        self.init_tasks = []
        self.cleanup_tasks = []
        self.getScenarioTimestamp()
        self.network_device = None
        self.create_scen_logs_dir()
        self.network_device = self.config.get("network")
        self.timeout = self.config.get("timeout", 0)
        self.tasks = self.config.create_task_set("tasks", self.file, self.controller, self, set_defaults_dict)
        self.init_tasks = self.config.create_task_set("init_tasks", self.file, self.controller, self, set_defaults_dict)
        self.cleanup_tasks = self.config.create_task_set("cleanup_tasks", self.file, self.controller, self, set_defaults_dict)

    def fetch_vars(self):
        """Check dictionary for custom variables in current test set"""
        if not VARIABLES in os.listdir(self.dirname):
            self.variables = None
            return None
        var_parser = parser.Parser()
        self.variables = var_parser.parse_yaml(os.path.join(self.dirname, VARIABLES))

    def create_scen_logs_dir(self):
        """Creates current scenario logs directory"""
        if not os.path.isdir(self.scen_logs_dir):
            os.mkdir(self.scen_logs_dir)

    def getNetwork(self):
        return self.network_device

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
        self.start_tcpdump()
        try:
            self.init()
            for task in self.tasks:
                task.run()
        except Exception:
            logger.slog.exception("Error occured during task run")
        try:
            self.cleanup()
        except Exception:
            logger.slog.exception("Error occured during cleanup task")
        self.wait_end()
        self.stop_tcpdump()
        self.getLogs()
        self.getStatus()
        self.verifyTest()

    def update(self):
        """updates the status of a scenario"""
        for tsk in self.tasks:
            tsk.update()

    def wait_end(self):
        """waits for all the tasks within a scenario to end"""
        wait = True
        counter = 0
        if self.timeout != 0:
            counter = self.timeout * 10; # 1000 ms / 100 (a cycle) -> 10 cycles per sec
        while wait or (self.timeout!=0 and counter==0):
            wait = False
            # see if we still have "running" "non-daemons"
            for tsk in reversed(self.tasks):
                if tsk.daemon == False and tsk.container.status != "exited":
                    wait = True
            if wait:
                time.sleep(0.1)  #sleep 100 ms before rechecking
                self.update()
                counter -= 1
        if wait:
            logger.slog.warning(" - WARNING: not all tasks self-terminated, end-forcing due timeout")
        # stop all remaining containers
        self.stopAll()

    def stop_tcpdump(self):
        """Stops started tcpdump"""
        if self.tcpdump:
            self.tcpdump.terminate()
        time.sleep(0.5)

    def stopAll(self):
        """Stops all the running tasks"""
        for tsk in self.tasks:
            if tsk.container.status != "exited":
                tsk.stop()
            logger.slog.debug("%s - ExitCode: %s", tsk.name, str(tsk.get_exit_code()))

    def getLogs(self):
        logs_path = self.scen_logs_dir
        for task in self.init_tasks:
            name = str(self.timestamp) + "_" + task.container.name
            log_file = os.path.join(logs_path, name)
            f = open(log_file, 'w')
            f.write(task.container.logs().decode('UTF-8'))
            f.close()
            logger.slog.debug(str(datetime.utcnow()) + " - Logs for {} fetched successfully!".format(task.container.name))
        for task in self.tasks:
            name = str(self.timestamp) + "_" + task.container.name
            log_file = os.path.join(logs_path, name)
            f = open(log_file, 'w')
            f.write(task.container.logs().decode('UTF-8'))
            f.close()
            logger.slog.debug(str(datetime.utcnow()) + " - Logs for {} fetched successfully!".format(task.container.name))
        for task in self.cleanup_tasks:
            name = str(self.timestamp) + "_" + task.container.name
            log_file = os.path.join(logs_path, name)
            f = open(log_file, 'w')
            f.write(task.container.logs().decode('UTF-8'))
            f.close()
            logger.slog.debug(str(datetime.utcnow()) + " - Logs for {} fetched successfully!".format(task.container.name))


    def start_tcpdump(self):
        """Starts a tcpdump for a scenario"""
        if not self.network_device or self.network_device == "host":
            res = "any"
        else:
            res = self.network_device
 
        directory = self.scen_logs_dir
        capture_file = os.path.join(directory, str(self.timestamp) + "_cap.pcap")
        self.tcpdump = subprocess.Popen(['tcpdump', '-i', res, '-w', capture_file],
                                         stdout=subprocess.DEVNULL,
                                         stderr=subprocess.DEVNULL)
        # wait for proc to start
        time.sleep(0.5)

    def getScenarioTimestamp(self):
        self.timestamp = int(datetime.utcnow().timestamp())

    def getStatus(self):
        logs_path = self.scen_logs_dir
        for task in self.tasks:
            name = str(self.timestamp) + "_" + task.container.name + "_STATUS"
            log_file = os.path.join(logs_path, name)
            f = open(log_file, 'w')
            f.write(task.container.name + " " + str(task.container.image) + " ExitCode: " + str(task.get_exit_code()))
            f.close()
            logger.slog.debug(str(datetime.utcnow())+ " - Status for {} fetched successfully!".format(task.container.name))

    def printStatus(self):
        for task in self.tasks:
            logger.slog.debug( "Name: {}, ExitCode: {}".format(task.container.name, str(task.get_exit_code())))

    def verifyTest(self):
        ok = True
        for task in self.tasks:
            if task.get_exit_code() != 0 and task.daemon == False:
                ok = False
                break
        if ok == False:
            logger.slog.debug(80*"=")
            logger.slog.info("Test: {}".format(os.path.basename(self.dirname)))
            self.printStatus()
            logger.slog.info( "TEST FAILED!")
            logger.slog.info(80*"=")
            self.tlogger.failed()
        else:
            logger.slog.debug(80*"=")
            logger.slog.info("Test: {}".format(os.path.basename(self.dirname)))
            self.printStatus()
            logger.slog.info("TEST PASSED!")
            logger.slog.info(80*"=")
            self.tlogger.success()

    def __del__(self):
        pass

# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

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

LOGS_DIR = "logs"
NETWORK_CAP = "net_capture"

class Scenario():

    """Class that implements running a scenario"""

    def __init__(self, file, config, controller, set_logs_dir):
        self.tcpdump = None
        self.controller = controller
        self.config = config
        self.file = file
        self.tlogger = controller.tlogger
        self.dirname = os.path.dirname(file)
        self.name = os.path.basename(self.dirname)
        self.scen_logs_dir = set_logs_dir + "/" + self.name
        self.tasks = []
        self.getScenarioTimestamp()
        self.network_device = None
        self.create_scen_logs_dir()

        if "network" in config.keys():
            self.network_device = config["network"]
        else:
            self.network_device = None

        if "timeout" in config.keys():
            self.timeout = config["timeout"]
        else:
            self.timeout = 0

        for key in config["tasks"]:
            if "type" in key.keys():
                task_type = key["type"].lower()
            else:
                # create a generic task
                task_type = ""

            new_task = None
            try:
                task_mod = getattr(
                        importlib.import_module("framework.tasks"),
                        task_type)
                normalized_task_type = "".join(
                        [ x for x in task_type if x.isalnum() ])
                normalized_class_name = normalized_task_type + "task"
                classes = [ c for c in dir(task_mod) if
                        c.lower() == normalized_class_name and
                        c.endswith("Task") ]
                if len(classes) == 0:
                    logger.slog.debug("unknown task derived from %s", task_type)
                elif len(classes) != 1:
                    logger.slog.debug("too many classed derived from %s: %s",
                                      task_type, str(classes))
                else:
                    class_name = getattr(task_mod, classes[0])
                    new_task = class_name(os.path.dirname(self.file),
                            key, self.controller, self)
            except AttributeError:
                logger.slog.debug("%s not found", task_type)

            if not new_task:
                logger.slog.debug("creating a generic task")
                new_task = task.Task(os.path.dirname(self.file),
                        key, self.controller, self)
            self.tasks.append(new_task)

    def create_scen_logs_dir(self):
        """Creates current scenario logs directory"""
        if not os.path.isdir(self.scen_logs_dir):
            os.mkdir(self.scen_logs_dir)

    def getNetwork(self):
        return self.network_device

    def init(self):
        """Runs the init tasks for a scenario"""
        for tsk in self.tasks:
            if str(tsk) == "initialTask":
                tsk.run()

    def cleanup(self):
        """Runs the cleanup tasks for a scenario"""
        for tsk in self.tasks:
            if str(tsk) == "cleanupTask":
                tsk.run()

    def run(self):
        """Runs a scenario with all its prerequisits"""
        self.tlogger.test_start(self.name)
        self.start_tcpdump()
        try:
            self.init()
            for tsk in self.tasks:
                if str(tsk) != "initialTask" and str(tsk) != "cleanupTask":
                    tsk.run()
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
        for task in self.tasks:
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

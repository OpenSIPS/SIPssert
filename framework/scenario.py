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
import docker
import importlib
import time
from framework import logger
from framework.tasks import task
from framework import logger
from datetime import datetime
import subprocess

LOGS_DIR = "logs"
NETWORK_CAP = "net_capture"

class Scenario():

				def __init__(self, file, config, controller):
								self.p = None
								self.controller = controller
								self.config = config
								self.file = file
								self.dirname = os.path.dirname(file)
								self.tasks = []
								self.getScenarioTimestamp()
								self.network_device = None

								if "network" in config.keys():
												self.network_device = config["network"]
								else:
												self.network_device = "default_device"

								if "timeout" in config.keys():
												self.timeout = config["timeout"]
								else:
												self.timeout = 0

								for e in config["tasks"]:
												if "type" in e.keys():
																task_type = e["type"].lower()
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
																				logger.slog.debug("unknown task derived from {}".
																												format(task_type))
																elif len(classes) != 1:
																				logger.slog.debug("too many classed derived from {}: {}".
																												format(task_type, str(classes)))
																else:
																				className = getattr(task_mod, classes[0])
																				new_task = className(os.path.dirname(self.file),
																												e, self.controller, self)
												except AttributeError:
																logger.slog.debug(task_type + " not found")
																pass

												if not new_task:
																logger.slog.debug("creating a generic task")
																try:
																				new_task = task.Task(os.path.dirname(self.file),
																												e, self.controller, self)
																except:
																				logger.slog.error("Could not create task for " + className)
												# TODO: sort out the tasks
												if new_task:
																self.tasks.append(new_task)

				def getTasks(self):
								return self.tasks

				def getNetwork(self):
								return self.network_device

				def init(self):
								for e in self.getTasks():
												if str(e) == "initialTask":
																e.run()

				def cleanup(self):
								for e in self.getTasks():
												if str(e) == "cleanupTask":
																e.run()

				def run(self):
								try:
												self.init()
												for e in self.getTasks():
																if True or str(e) != "initialTask" and str(e) != "cleanupTask":
																				e.run()
								except:
												logger.slog.error("Something happened")
								self.cleanup()

				def update(self):
								for e in self.getTasks():
												e.update()

				def waitEnd(self):
								wait = True
								counter = 0
								if self.timeout != 0:
												counter = self.timeout * 10; # 1000 ms / 100 (a cycle) -> 10 cycles per sec
								while wait or (self.timeout!=0 and counter==0):
												wait = False
												# see if we still have "running" "non-daemons"
												for e in reversed(self.getTasks()):
																if e.daemon == False and e.container.status != "exited":
																				wait = True
												if wait:
																time.sleep(0.1)  #sleep 100 ms before rechecking
																self.update()
																counter -= 1
								if wait:
												logger.slog.warning(" - WARNING: not all tasks self-terminated, end-forcing due timeout");
								# stop all remaining containers
								self.stopAll()

				def stopTcpdump(self):
								if self.p:
												#logger.slog.info(str(datetime.utcnow()) +" - Tcpdump ended!")
												self.p.terminate()
								time.sleep(0.5)

				def stopAll(self):
								for e in self.getTasks():
												if e.container.status != "exited":
																#e.stop()
																logger.slog.debug(str(datetime.utcnow()) +" "+ e.name+ " - ExitCode: "+ str(e.get_exit_code()))
												else:
																logger.slog.debug(str(datetime.utcnow()) +" "+ e.name+ " - ExitCode: "+ str(e.get_exit_code()))


				def createDir(self, dir, searching_dir):
								if searching_dir not in os.listdir(dir):
												path = os.path.join(dir, searching_dir)
												os.mkdir(path)
												logger.slog.debug(str(datetime.utcnow()) + " - {} dir created successfully!".format(searching_dir))
								else:
												logger.slog.debug(str(datetime.utcnow()) + " - {} dir already exists!".format(searching_dir))

				def getLogs(self):
								self.createDir(self.dirname, LOGS_DIR)
								logs_path = os.path.join(self.dirname, LOGS_DIR)
								for task in self.tasks:
												name = "test" + str(self.timestamp) + "_" + task.container.name
												log_file = os.path.join(logs_path, name)
												f = open(log_file, 'w')
												f.write(task.container.logs().decode('UTF-8'))
												f.close()
												logger.slog.debug(str(datetime.utcnow()) + " - Logs for {} fetched successfully!".format(task.container.name))

				def startTcpdump(self):
								if self.network_device == "host":
												res = "any"
								else:
												res = self.network_device
												
								self.createDir(self.dirname, LOGS_DIR)
								dir = os.path.join(self.dirname, LOGS_DIR)
								capture_file = os.path.join(dir, str(self.timestamp) + "_cap.pcap")
								self.p = subprocess.Popen(['tcpdump', '-i', res, '-w', capture_file], stdout=subprocess.PIPE)
								# wait for proc to start
								time.sleep(0.5)

				def getScenarioTimestamp(self):
								self.timestamp = int(datetime.utcnow().timestamp())

				def getStatus(self):
								self.createDir(self.dirname, LOGS_DIR)
								logs_path = os.path.join(self.dirname, LOGS_DIR)
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
								else:
												logger.slog.debug(80*"=")
												logger.slog.info("Test: {}".format(os.path.basename(self.dirname)))
												self.printStatus()
												logger.slog.info("TEST PASSED!")
												logger.slog.info(80*"=")

				def __del__(self):
								pass
												

# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

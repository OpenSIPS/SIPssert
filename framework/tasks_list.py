#!/usr/bin/env pyth
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
import time
import importlib
from framework import logger

"""Implements the behavior of a list of tasks"""

class TasksList(list):
    """Handles a list of Tasks"""

    def __init__(self, task_set_key, task_dir, logs_dir,
            config, controller, defaults=None):
        super().__init__([])
        self.timeout = 0
        self.running_tasks = []
        if task_set_key not in config:
            return
        for definition in config[task_set_key]:
            task = self.create_task(definition,
                    task_dir, logs_dir, controller, defaults)
            if task:
                self.append(task)

    def set_timeout(self, timeout):
        self.timeout = timeout

    def run(self, force_all=False, wait=True):
        exc = None
        logger.slog.debug("running tasks {}".format(self))
        for task in self:
            try:
                task.run()
                self.running_tasks.append(task)
            except Exception as e:
                if not force_all:
                    exc = e
                    break
        if wait:
            self.wait()
        if exc:
            raise exc

    def wait(self):
        """waits for all the tasks within a scenario to end"""
        if len(self.running_tasks) == 0:
            return
        logger.slog.debug("waiting for run tasks {}".format(self.running_tasks))
        wait = True
        counter = 0
        if self.timeout != 0:
            counter = self.timeout * 10; # 1000 ms / 100 (a cycle) -> 10 cycles per sec
        while wait or (self.timeout!=0 and counter==0):
            wait = False
            # see if we still have "running" "non-daemons"
            for tsk in reversed(self.running_tasks):
                if tsk.daemon == True:
                    continue
                if not tsk.has_ended():
                    wait = True
            if wait:
                time.sleep(0.1)  #sleep 100 ms before rechecking
                counter -= 1
        if wait:
            logger.slog.warning("not all tasks self-terminated, end-forcing due timeout")
        # stop all remaining containers, including daemons
        for tsk in self.running_tasks:
            if not tsk.has_ended():
                tsk.stop()
            tsk.finish()

    def create_task(self, definition, task_dir, logs_dir,
            controller, defaults=None):
        """Creates a task based on its definition"""
        if definition["type"] in defaults.keys():
            definition = defaults[definition["type"]] | definition
        if "type" in definition.keys():
            task_type = definition["type"].lower()
        else:
            # create a generic task
            task_type = "generic"

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
                new_task = class_name(definition)
                new_task.set_logs_dir(logs_dir)
                new_task.add_volume_dir(os.path.dirname(task_dir))
                new_task.create(controller)
                return new_task
        except AttributeError:
            raise Exception(f"unknown task type {task_type}")
        return None

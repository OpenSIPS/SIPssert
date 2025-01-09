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


"""Implements the behavior of a list of tasks"""

import time
import importlib
from sipssert import logger
from sipssert.task import State
from sipssert.testing import TestStatus
from sipssert.config import ConfigLevel

TIMEOUT_GRANULARITY = 0.1 # seconds

class TasksList(list):
    """Handles a list of Tasks"""

    def __init__(self, task_set_key, task_dir, logs_dir,
            config, controller, network, networks, container_prefix=None, defaults={}):
        super().__init__([])
        self.timeout = 0
        self.status = TestStatus.UNKN
        self.task_dir = task_dir
        self.logs_dir = logs_dir
        self.network = network
        self.networks = networks
        self.controller = controller
        self.container_prefix = container_prefix
        self.defaults = defaults
        self.daemon_tasks = []
        self.running_tasks = []
        self.pending_tasks = []
        if task_set_key not in config:
            return
        for definition in config[task_set_key]:
            if self.network and "network" not in definition:
                definition["network"] = self.network
            if self.networks and "networks" not in definition:
                definition["networks"] = self.networks
            task = self.create_task(definition)
            if task:
                self.append(task)
                self.pending_tasks.append(task)

    def set_timeout(self, timeout):
        self.timeout = timeout

    def get_tasks_to_run(self, current_time):
        tasks_to_run = []
        for tsk in self.pending_tasks:
            if tsk.state == State.CREATED and \
                    tsk.satisfied(self, current_time):
                tasks_to_run.append(tsk)
        return tasks_to_run

    def get_task_by_container(self, container_name):
        for tsk in self:
            if tsk.container_name == container_name:
                return tsk
        return None

    def get_task(self, name):
        for tsk in self:
            if tsk.match(name):
                return tsk
        return None

    def update_status(self, status):
        if self.status == TestStatus.UNKN or status > self.status:
            self.status = status

    def handle_events(self, start, stop):
        #logger.slog.debug("handling events from {} to {}".format(start, stop))
        for event in self.controller.docker.events(start, stop, decode=True):
            if event['Type'] != "container":
                continue
            attrs = event['Actor']['Attributes']
            name = attrs['name']
            tsk = self.get_task_by_container(name)
            if not tsk:
                # suppress events of tasks not owned by us
                #logger.slog.warning("event {} for unknown task {}".
                #                    format(event, name))
                continue
            # fetch the task
            if event["Action"] == "die":
                # a container was stopped
                if tsk.has_finished:
                    pass
                logger.slog.debug("handing stop event for {}".format(name))
                tsk.finish()
                status = int(attrs["exitCode"])
                self.update_status(TestStatus.PASS if status == 0 and tsk.logs_ok else TestStatus.FAIL)
                if status != 0:
                    logger.slog.error(f"{name} failed with exit code {status}")
                if tsk.daemon:
                    self.daemon_tasks.remove(tsk)
                else:
                    self.running_tasks.remove(tsk)

    def terminate(self, exc):
        if len(self.pending_tasks) > 0:
            logger.slog.warning("tasks {} not scheduled".
                    format(self.pending_tasks))
        if len(self.running_tasks) > 0:
             logger.slog.warning("remaining tasks {}".
                        format(self.running_tasks))
        for tsk in self.running_tasks:
            logger.slog.warning("forcefully stopping {}".format(tsk))
            tsk.stop()
            tsk.finish()
            self.update_status(TestStatus.TOUT)

        for tsk in reversed(self.daemon_tasks):
            tsk.stop()
            tsk.finish()
            status = tsk.get_exit_code()
            self.update_status(TestStatus.PASS if status == 0 and tsk.logs_ok else TestStatus.FAIL)

        if exc:
            logger.slog.error(exc)
            self.update_status(TestStatus.FAIL)

    def run(self, force_all=False):
        self.start_time = time.time()
        last_events_time = self.start_time
        exc = None
        while (len(self.pending_tasks) > 0 or len(self.running_tasks) > 0) and exc is None:

            current_time = time.time()
            self.handle_events(last_events_time, current_time)
            last_events_time = current_time
            tasks_to_run = self.get_tasks_to_run(current_time)
            if len(tasks_to_run) > 0:
                logger.slog.debug("running tasks {}".format(tasks_to_run))
            for task in tasks_to_run:
                try:
                    task.run()
                    if task.daemon:
                        self.daemon_tasks.append(task)
                    else:
                        self.running_tasks.append(task)
                except Exception as e:
                    if not force_all:
                        exc = e
                        break
                self.pending_tasks.remove(task)
            if exc:
                break
            # if there are no other pending tasks, check to see if
            # we have any more non-daemon tasks to run
            finish_time = time.time()
            if self.timeout and finish_time - self.start_time >= self.timeout:
                logger.slog.warning("timeout {} reached".
                        format(self.timeout))
                break
            else:
                timeout = TIMEOUT_GRANULARITY - finish_time - current_time
                if timeout > 0:
                    time.sleep(timeout)

        self.terminate(exc)
        if len(self) > 0:
            logger.slog.debug("finished running tasks {}".format(self))
            logger.slog.debug("tasks executed in {:.3f}s".format(time.time() - self.start_time))

    def merge_dicts(self, dict1, dict2):
        """
        Recursive merge dictionaries.

        :param dict1: Base dictionary to merge.
        :param dict2: Dictionary to merge on top of base dictionary.
        :return: Merged dictionary
        """
        for key, val in dict1.items():
            if isinstance(val, dict):
                dict2_node = dict2.setdefault(key, {})
                self.merge_dicts(val, dict2_node)
            else:
                if key not in dict2:
                    dict2[key] = val

        return dict2


    def create_task(self, definition):
        """Creates a task based on its definition"""
        if "type" in definition.keys():
            task_type = definition["type"].lower()
        else:
            # create a generic task
            task_type = "generic"
        if task_type in self.defaults.keys():
            definition = ConfigLevel(self.merge_dicts(self.defaults[task_type], dict(definition)))

        try:
            task_mod = getattr(
                    importlib.import_module("sipssert.tasks"),
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
                new_task = class_name(self.task_dir, definition)
                new_task.set_logs_dir(self.logs_dir)
                new_task.add_volume_dir(self.task_dir)
                new_task.create(self.controller, self.container_prefix)
                return new_task
        except AttributeError:
            raise Exception(f"unknown task type {task_type}")
        return None

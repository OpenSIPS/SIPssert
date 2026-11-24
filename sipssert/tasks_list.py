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

import queue
import threading
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
            config, controller, network, networks, volumes, task_templates={}, container_prefix=None, defaults={}):
        super().__init__([])
        self.timeout = 0
        self.status = TestStatus.UNKN
        self.task_dir = task_dir
        self.logs_dir = logs_dir
        self.network = network
        self.networks = networks
        self.volumes = volumes
        self.controller = controller
        self.container_prefix = container_prefix
        self.defaults = defaults
        self.daemon_tasks = []
        self.running_tasks = []
        self.pending_tasks = []
        self._event_queue = None
        self._event_thread = None
        self._event_gen = None
        self._event_started = threading.Event()
        self.task_templates = task_templates
        if task_set_key not in config:
            return
        for definition in config[task_set_key]:
            if self.network and "network" not in definition:
                definition["network"] = self.network
            if self.networks and "networks" not in definition:
                definition["networks"] = self.networks
            if "volumes" in definition:
                if isinstance(definition["volumes"], list):
                    complete_def = {}
                    for vol in definition["volumes"]:
                        if vol not in self.volumes:
                            if not self.controller.docker.volumes.get(vol):
                                raise Exception(f"volume {vol} not defined in scenario or outside of it")
                            # if the volume is defined outside of the scenario, but is passed in a list,
                            # we don't know `bind` and `mode` keys, so we raise an exception
                            raise Exception(f"volume {vol} incomplete declared: use 'bind' and 'mode' keys")
                        else:
                            complete_def[vol] = self.volumes[vol]
                        if "bind" not in complete_def[vol] or "mode" not in complete_def[vol]:
                            raise Exception(f"volume {vol} incomplete defined")
                    definition["volumes"] = complete_def
                elif isinstance(definition["volumes"], dict):
                    for vol in definition["volumes"]:
                        if vol not in self.volumes:
                            if not self.controller.docker.volumes.get(vol):
                                raise Exception(f"volume {vol} not defined in scenario or outside of it")
                            self.volumes[vol] = {}

                        if definition["volumes"][vol] is None:
                            definition["volumes"][vol] = {}

                        # if the volume is declared as a dict, it should have 'bind' and 'mode' keys
                        definition["volumes"][vol].setdefault("bind", self.volumes[vol].get("bind", None))
                        definition["volumes"][vol].setdefault("mode", self.volumes[vol].get("mode", None))

                        if definition["volumes"][vol]["bind"] is None or definition["volumes"][vol]["mode"] is None:
                            raise Exception(f"volume {vol} incomplete defined")
                else:
                    raise Exception(f"volumes should be a list or a dictionary")
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

    def handle_events(self):
        if not self._event_queue:
            return
        while True:
            try:
                event = self._event_queue.get_nowait()
            except queue.Empty:
                return
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

    def _start_event_stream(self):
        """Starts a single live docker events stream, pumped into a queue.

        The previous implementation polled windowed
        docker.events(since, until) calls on every scheduling iteration.
        The `until` argument makes the docker daemon hold the HTTP stream
        open until that wall-clock time is reached by the daemon itself,
        so any clock skew between the host and the docker daemon (common
        with desktop hypervisors after host sleep) blocked the scheduling
        loop for the whole duration of the skew. Moreover, event
        timestamps follow the daemon clock and, filtered against
        host-clock windows, were systematically missed. A single live
        stream consumed by a background thread depends on no clock
        arithmetic at all.
        """
        self._event_queue = queue.Queue()

        def pump():
            try:
                gen = self.controller.docker.events(decode=True)
            except Exception:
                self._event_started.set()
                return
            self._event_gen = gen
            self._event_started.set()
            try:
                for event in gen:
                    self._event_queue.put(event)
            except Exception:
                pass

        self._event_thread = threading.Thread(target=pump, daemon=True)
        self._event_thread.start()

    def _stop_event_stream(self):
        self._event_started.wait(timeout=2)
        gen = self._event_gen
        if gen is not None:
            try:
                gen.close()
            except Exception:
                pass
        self._event_thread.join(timeout=2)
        self._event_queue = None

    def terminate(self, exc):
        if len(self.pending_tasks) > 0:
            logger.slog.warning("tasks {} not scheduled".
                    format(self.pending_tasks))
        if len(self.running_tasks) > 0:
             logger.slog.warning("remaining tasks {}".
                        format(self.running_tasks))
        for tsk in self.running_tasks:
            logger.slog.warning("forcefully stopping {}".format(tsk))
            try:
                tsk.stop()
                tsk.finish()
            except Exception:
                logger.slog.exception("error while stopping task {}".format(tsk))
            self.update_status(TestStatus.TOUT)

        for tsk in reversed(self.daemon_tasks):
            try:
                tsk.stop()
                tsk.finish()
                status = tsk.get_exit_code()
                self.update_status(TestStatus.PASS if status == 0 and tsk.logs_ok else TestStatus.FAIL)
            except Exception:
                logger.slog.exception("error while stopping daemon task {}".format(tsk))
                self.update_status(TestStatus.FAIL)

        if exc:
            logger.slog.error(exc)
            self.update_status(TestStatus.FAIL)

    def run(self, force_all=False):
        self.start_time = time.time()
        self._event_started.clear()
        self._start_event_stream()
        try:
            exc = None
            while (len(self.pending_tasks) > 0 or len(self.running_tasks) > 0) and exc is None:

                current_time = time.time()
                self.handle_events()
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
                    timeout = TIMEOUT_GRANULARITY - (finish_time - current_time)
                    if timeout > 0:
                        time.sleep(timeout)
        finally:
            self._stop_event_stream()

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
        tmpl_key = None
        if "type" in definition.keys():
            task_type = definition["type"].lower()
            if task_type in self.task_templates:
                tmpl_key = task_type
                definition.pop("type")
        elif "use" in definition.keys():
            tmpl_key = definition["use"].lower()
            if tmpl_key not in self.task_templates:
                raise Exception(f"unknown task template {tmpl_key}")

        if tmpl_key:
            template_def = self.task_templates[tmpl_key]
            definition = self.merge_dicts(dict(template_def), dict(definition))

        task_type = definition.get("type", "generic").lower()

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

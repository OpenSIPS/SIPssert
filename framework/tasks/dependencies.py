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

"""Implements the logic of a task dependencies"""

from framework import logger
from framework.tasks.task import State

class TaskDep:
    """Holds information about a task dependency"""

    def satisfied(self, task, task_list, current_time):
        """returns true of dependency is satisfied or false otherwise"""
        raise Exception("dependency not implemented!")

class TaskDepAfter(TaskDep):
    """Implements the 'After' dependency"""

    def __init__(self, info):
        self.wait = 0
        self.warned = False
        if isinstance(info, dict):
            # if it is a dictionary, it may have a wait
            # convert all keys to lower
            keys_dict = { k.lower(): k for k in info.keys() }
            self.task_name = info[keys_dict["task"]]
            if "wait" in keys_dict:
                self.wait = float(info[keys_dict["wait"]])
        else:
            # this must be a string, and represents the name of the task
            self.task_name = info

    def satisfied(self, task, task_list, current_time, active = False):
        """returns true if task_name has finished"""
        task_dep = task_list.get_task(self.task_name)
        if not task_dep:
            if not self.warned:
                logger.slog.warn("could not find task '{}'".format(self.task_name))
                self.warned = True
            return False
        # if not started yet, dependency is not fulfilled
        if task_dep.daemon or active:
          if task_dep.state < State.ACTIVE:
            return False
          relative_time = task_dep.start_time
        else:
          if task_dep.state < State.ENDED:
             return False
          relative_time = task_dep.end_time
        if self.wait != 0 and current_time - relative_time < self.wait:
            return False
        return True

class TaskDepStarted(TaskDepAfter):
    """Implements the 'Started' dependency"""

    def satisfied(self, task, task_list, current_time):
        return super().satisfied(task, task_list, current_time, True)

class TaskDepWait(TaskDep):
    """Implements the 'Wait' dependency"""

    def __init__(self, wait):
        self.wait = float(wait)

    def satisfied(self, task, task_list, current_time):
        """waits for wait time from run start""" 
        return current_time - task_list.initial_time >= self.wait

class TaskDepDelay(TaskDep):
    """Implements the 'Delay' dependency"""

    def __init__(self, wait):
        self.wait = float(wait)

    def satisfied(self, task, task_list, current_time):
        """delays the start after previous task has been run"""
        # find the previous task
        tsk_prev = None
        for tsk_tmp in task_list:
            if task == tsk_tmp:
                break
            tsk_prev = tsk_tmp
        if not tsk_prev:
            relative_time = task_list.initial_time
        elif tsk_prev.state < State.ACTIVE or not tsk_prev.start_time:
            return False
        else:
            relative_time = tsk_prev.start_time
        return current_time - relative_time >= self.wait

def parse_dependencies(deps):
    """Parses the dependencies nodes of a task"""
    if not deps:
        return []
    # convert to a 1-element list
    if not isinstance(deps, list):
        deps = [ deps ]
    dependencies = []
    for dep in deps:
        if isinstance(dep, dict): # if just a string, it's a dependency of After
            # convert all keys to lower
            keys_dict = { k.lower(): k for k in dep.keys() }

            if "after" in keys_dict:
                td = TaskDepAfter(dep[keys_dict["after"]])
            elif "delay" in keys_dict:
                td = TaskDepDelay(dep[keys_dict["delay"]])
            elif "started" in keys_dict:
                td = TaskDepStarted(dep[keys_dict["started"]])
            elif "wait" in keys_dict:
                td = TaskDepWait(dep[keys_dict["wait"]])
            else:
                raise Exception("Unknown dependency {}".format(dep))
            if td:
                dependencies.append(td)
        else:
            dependencies.append(TaskDepAfter(dep))
    return dependencies

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
import importlib
from framework import logger

"""Helpers for parsing tasks"""

def get_network(config):
    """Returns the network provided by a config"""
    return None

def create_task(definition, file_name, controller, defaults=None):
    """Creates a task based on its definition"""
    if definition["type"] in defaults.keys():
        definition = defaults[definition["type"]] | definition
    if "type" in definition.keys():
        task_type = definition["type"].lower()
    else:
        # create a generic task
        task_type = "generic"

    if task_type == "generic":
        logger.slog.debug("creating a generic task")
        new_task = task.Task(os.path.dirname(file_name),
                definition, controller)
        return new_task
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
            new_task = class_name(os.path.dirname(file_name),
                    definition, controller)
            return new_task
    except AttributeError:
        raise Exception(f"unknown task type {task_type}")
    return None

def create_task_list(task_set_key, file_name, config, controller, defaults=None):
    """Creates a list of tasks"""
    task_set = []
    if task_set_key not in config:
        return task_set
    for definition in config[task_set_key]:
        task = create_task(definition, file_name, controller, defaults)
        if task:
            task_set.append(task)
    return task_set

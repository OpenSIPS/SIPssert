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
import configparser
from framework import parser

"""Implements config layer"""

class FrameworkConfig:

    def __init__(self, config_file, dictionary = False):
        if dictionary:
            self.config = config_file
        else:
            config_parser = parser.Parser()
            self.config = config_parser.parse_yaml(config_file)
        self.dynamic_options = {}

    def get(self, key):
        if key in self.dynamic_options.keys():  
            return self.dynamic_options[key]
        elif key in self.config.keys():
            return self.config[key]
        else:
            return None

    def get_or_default(self, key, default=None):
        if key in self.dynamic_options.keys():
            return self.dynamic_options[key]
        elif key in self.config.keys():
            return self.config[key]
        else:
            return default

    def get_extra_params(self):
        if "extra_params" in self.config:
            extra_params = self.config["extra_params"].split(" ")
        else:
            extra_params = []
        return extra_params

    def get_config_file(self, default_mount_point=None):
        if "config_file" in self.config:
            # if an absolute path, leave it as it is
            if os.path.isabs(self.config["config_file"]):
                self.config_file = self.config["config_file"]
            else:
                # path is relative to the mount point
                self.config_file = os.path.join(self.get_or_default("mount_point", default_mount_point),
                self.config["config_file"])
        else:
            self.config_file = None
        return self.config_file



    def get_ports(self):
        r = {}
        if "ports" in self.config:
            for p in self.config["ports"]:
                port, proto = p.split("/")
                r[p] = port
        return r
    
    def get_nets(self):
        return self.config["networks"] if self.config and "networks" in self.config else None

    def set(self, key, value):
        self.dynamic_options[key] = value

    def create_task_set(self, task_set_key, task_set):
        task_set = []
        if task_set_key not in self.config:
            return
        for key in self.config[task_set_key]:
            if "type" in key.keys():
                task_type = key["type"].lower()
            else:
                # create a generic task
                task_type = ""

            if task_type == "" or task_type == "generic":
                logger.slog.debug("creating a generic task")
                new_task = task.Task(os.path.dirname(self.file),
                        key, self.controller, self)
                task_set.append(new_task)
                return
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
                    task_set.append(new_task)
            except AttributeError:
                logger.slog.error("unknown task type %s", task_type)
                raise Exception("unknown task type {task_type}")
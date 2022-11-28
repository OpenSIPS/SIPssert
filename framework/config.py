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
import configparser
import importlib
import yaml
import jinja2
from framework import logger

"""Implements config layer"""

class ConfigParseError(yaml.YAMLError):
    """Throws exception when cannot parse yaml file"""
    pass

class ConfigParamNotFound(Exception):
    """Throws exception when a parameter cannot be found"""
    def __init__(self, param):
        super().__init__(f"mandatory param {param} not found")

class ConfigLevel(dict):

    """Implements one level of configuration"""

    def get(self, key, default=None, mandatory=False):
        """Returns a level or a key"""
        if key in self.keys():
            d = super().__getitem__(key)
        elif mandatory:
            raise ConfigParamNotFound(key)
        else:
            return default
        if type(d) is dict:
            return ConfigLevel(d)
        else:
            return d

    def __getitem__(self, key):
        """Returns a mandatory key or a section from the config"""
        return self.get(key, None, True)

class Config:

    """Implements the basic configuration class"""

    def __init__(self, config_file_or_dir, config_file = None, template_file = None, template_vars = {}):
        if config_file:
            self.config_dir = config_file_or_dir
            self.config_file = config_file
        else:
            self.config_dir = os.path.dirname(config_file_or_dir)
            self.config_file = os.path.basename(config_file_or_dir)
        if template_file and template_file in os.listdir(self.config_dir):
            self.template_file = template_file
            self.template_file_path = os.path.join(self.config_dir, template_file)
            self.defines = template_vars | \
                    self.parse(self.template_file_path, template_vars)
        else:
            self.template_file = None
            self.template_file_path = None
            self.defines = template_vars
        if not self.config_file in os.listdir(self.config_dir):
            self.config_file = None
            self.config_file_path = None
            self.config = ConfigLevel({})
        else:
            self.config_file_path = os.path.join(self.config_dir, self.config_file)
            self.config = ConfigLevel(self.parse(self.config_file_path, self.defines))

    def parse(self, yaml_file, template_vars=None):
        """Parses a yaml file, expanding templates"""
        yaml_stream = None
        with open(yaml_file, 'r') as stream:
            res = stream.read()
            if template_vars:
                environment = jinja2.Environment()
                template = environment.from_string(res)
                res = template.render(template_vars)
            try:
                yaml_stream = yaml.safe_load(res)
            except yaml.YAMLError as exc:
                raise ConfigParseError(exc)
        return yaml_stream

    def __getitem__(self, key):
        """Returns a key or a section from the config"""
        return self.config.get(key, None, True)

    def get(self, key, default=None, mandatory=False):
        """Returns a key or a section from the config"""
        return self.config.get(key, default, mandatory)

    def get_defines(self):
        """Returns all the variables defined"""
        return self.defines


    def get_extra_params(self):
        if "extra_params" in self.config:
            extra_params = self.config["extra_params"].split(" ")
        else:
            extra_params = []
        return extra_params

    def get_ports(self):
        r = {}
        if "ports" in self.config:
            for p in self.config["ports"]:
                port, proto = p.split("/")
                r[p] = port
        return r
    
    def get_nets(self):
        return self.config["networks"] if self.config and "networks" in self.config else None

    def create_task_set(self, task_set_key, fileName, controller, scenario, defaults=None):
        task_set = []
        if task_set_key not in self.config:
            return task_set
        for key in self.config[task_set_key]:
            if key["type"] in defaults.keys():
                key = defaults[key["type"]] | key
            if "type" in key.keys():
                task_type = key["type"].lower()
            else:
                # create a generic task
                task_type = ""

            if task_type == "" or task_type == "generic":
                logger.slog.debug("creating a generic task")
                new_task = task.Task(os.path.dirname(fileName),
                        self.config, controller, scenario.getNetwork())
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
                    new_task = class_name(os.path.dirname(fileName),
                            self.config, controller, scenario.getNetwork())
                    task_set.append(new_task)
            except AttributeError:
                raise Exception(f"unknown task type {task_type}")
        return task_set

    def create_test_set_tasks(self, task_set_key, fileName, controller, defaults=None):
        task_set = []
        if task_set_key not in self.config:
            return task_set
        task_set_tasks = self.config[task_set_key]
        for key in task_set_tasks:
            if key["type"] in defaults.keys():
                key = defaults[key["type"]] | key
            if "type" in key.keys():
                task_type = key["type"].lower()
            else:
                # create a generic task
                task_type = ""

            if task_type == "" or task_type == "generic":
                logger.slog.debug("creating a generic task")
                new_task = task.Task(os.path.dirname(fileName),
                        key, controller, "host")
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
                    new_task = class_name(os.path.dirname(fileName),
                            key, controller, "host")
                    task_set.append(new_task)
            except AttributeError:
                raise Exception(f"unknown task type {task_type}")
        return task_set

    def get_defaults(self):
        defaults = {}
        if 'defaults' in self.config.keys():
            for image_defaults in self.config['defaults']:
                defaults[image_defaults['type']] = image_defaults['values']
        return defaults

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

    def __contains__(self, key):
        """checkes whether a key is part of the config"""
        return key in self.config

    def get(self, key, default=None, mandatory=False):
        """Returns a key or a section from the config"""
        return self.config.get(key, default, mandatory)

    def get_defines(self):
        """Returns all the variables defined"""
        return self.defines

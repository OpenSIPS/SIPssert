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

import yaml
import jinja2

SCENARIO = "scenario.yml"
LOGS_DIR = "logs"

class Parser():

    def __init__(self):
        pass
    
    def parse_yaml(self, yaml_file):
        yaml_stream = None
        with open(yaml_file, 'r') as stream:
            try:
                yaml_stream = yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                logger.slog.error(exc)

        return yaml_stream
    
    def parse_yaml_template(self, yaml_file, template_vars):
        yaml_stream = None
        environment = jinja2.Environment()
        with open(yaml_file, 'r') as stream:
            data = stream.read()
            template = environment.from_string(data)
            res = template.render(template_vars)
            try:
                yaml_stream = yaml.safe_load(res)
            except yaml.YAMLError as exc:
                logger.slog.error(exc)
        return yaml_stream

# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

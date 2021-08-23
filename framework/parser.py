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

from framework import scenario
import os
import yaml
from datetime import datetime

SCENARIO = "scenario.yml"
LOGS_DIR = "logs"

class Parser():

    def __init__(self, list_test_dirs):
        self.list_test_dirs = list_test_dirs
        #self.root_path = root_path
        self.scenarios = None
        self.scenario_files = None

    def get_scenarios(self):

        if not self.scenario_files:
            self.scenario_files = []
            for test_dirs in self.list_test_dirs:
                for scenario_dir in os.listdir(test_dirs):
                    test_dir = os.path.join(test_dirs, scenario_dir)
                    if SCENARIO in os.listdir(test_dir):
                        self.scenario_files.append(os.path.join(test_dir,
                            SCENARIO))

        return self.scenario_files

    def parse_scenario_configs(self):

        self.get_scenarios()

        if not self.scenarios:
            self.scenarios = []
            for scenario in self.scenario_files:
                with open(scenario, 'r') as stream:
                    try:
                        cfg_stream = yaml.safe_load(stream)
                        self.scenarios.append((scenario, cfg_stream))
                    except yaml.YAMLError as exc:
                        print(exc)

        return self.scenarios


# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

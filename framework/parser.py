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
from framework import tests_set

SCENARIO = "scenario.yml"
LOGS_DIR = "logs"

class Parser():

    def __init__(self):
        pass

    # def get_sets(self):
    #     for set in self.list_test_dirs:
    #         set_scenarios = []
    #         for test in os.listdir(set):
    #             test_dir = os.path.join(set, test)
    #             if os.path.isdir(test_dir):
    #                 if SCENARIO in os.listdir(test_dir):
    #                     set_scenarios.append(os.path.join(test_dir, SCENARIO))

    #         self.sets.append(testSet.TestSet(os.path.basename(set), set_scenarios))

    # def parse_set_scenarios(self, set):
    #     scenarios = []
    #     for scenario in set.getSetScenarios():
    #         with open(scenario, 'r') as stream:
    #             try:
    #                 cfg_stream = yaml.safe_load(stream)
    #                 scenarios.append((scenario, cfg_stream))
    #             except yaml.YAMLError as exc:
    #                 print(exc)

    #     return scenarios
    
    def parse_yaml(self, yaml_file):
        yaml_stream = None
        with open(yaml_file, 'r') as stream:
            try:
                yaml_stream = yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                print(exc)

        return yaml_stream


# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

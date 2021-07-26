#!/usr/bin/env python
##
## TODO: update project's name
## (see https://github.com/OpenSIPS/opensips-cli).
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
import yaml
from framework import entity

SCENARIO = "scenario.yml"

class Parser():

    def __init__(self, root_path):
        self.root_path = root_path
        self.scenarios = None
        self.scenario_files = None

    def get_scenarios(self):

        if not self.scenario_files:
            self.scenario_files = []
            for scenario_dir in os.listdir(self.root_path):
                test_dir = os.path.join(self.root_path, scenario_dir)
                if SCENARIO in os.listdir(test_dir):
                    self.scenario_files.append(os.path.join(test_dir,
                        SCENARIO))

        return self.scenario_files

    def parse_scenarios(self):

        self.get_scenarios()

        if not self.scenarios:
            self.scenarios = []
            for scenario in self.scenario_files:
                with open(scenario, 'r') as stream:
                    try:
                        cfg_stream = yaml.safe_load(stream)
                        self.scenarios.append(cfg_stream)
                    except yaml.YAMLError as exc:
                        print(exc)

        return self.scenarios




    def setPorts(self, ports):
        dict = {}
        for p in ports:
            port, type = p.split("/")
            dict[p] = port

        return dict
            

    def streamToEntities(self, stream, entities):
        for e in stream["entities"]:
            if e["type"] == "uas-sipp":
                if "extra_params" in e.keys():
                    extra_params = e["extra_params"]
                else:
                    extra_params = ""
                container = entity.Entity_uas(e["name"], e["type"], e["image"], e["ports"], e["ip"])
                container.setExtraParams(extra_params)
                entities.append(container)
            elif e["type"] == "uac-sipp":
                if "extra_params" in e.keys():
                    extra_params = e["extra_params"]
                else:
                    extra_params = ""
                container = entity.Entity_uac(e["name"], e["type"], e["image"], e["ports"], e["ip"])
                container.setExtraParams(extra_params)
                entities.append(container)
            elif e["type"] == "opensips":
                if "extra_params" in e.keys():
                    extra_params = e["extra_params"]
                else:
                    extra_params = ""
                container = entity.Entity_opensips(e["name"], e["type"], e["image"], e["ports"], e["ip"])
                container.setExtraParams(extra_params)
                container.setMountPoint(e["mount_point"])
                container.setPathConfig(e["path_config"])
                container.setConfigFile(e["config_file"])
                entities.append(container)
            else:
                pass


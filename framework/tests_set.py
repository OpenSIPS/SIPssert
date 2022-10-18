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

"""Logic that runs a set of tests"""

import os
from framework import parser
from framework import scenario
from framework.network import network

SCENARIO = "scenario.yml"
CONFIG = "config.yml"

class TestSet():

    """Main class that runs a set of tests"""

    def __init__(self, set_path, controller, test):
        self.tests_to_run = test
        self.name = os.path.basename(set_path)
        self.set_path = set_path
        self.controller = controller
        self.parse_config()
        self.setup_networks()
        self.set_scenarios()

    def parse_config(self):
        """Parses tests set configuration file"""
        if not CONFIG in os.listdir(self.set_path):
            self.config = None
            return
        config_parser = parser.Parser()
        self.config = config_parser.parse_yaml(os.path.join(self.set_path, CONFIG))

    def get_network(self, name):
        """returns a created network based on its name"""
        if not name:
            return self.networks[0]
        network_list = [ net for net in self.networks if name == net.name ]
        if len(network_list) != 1:
            return None
        return network_list[0]

    def setup_networks(self):
        """Setup of all networks involved in the test set"""
        nets = self.config["networks"] if self.config and "networks" in self.config else None
        self.networks = network.get_networks(self.controller, nets)

    def set_scenarios(self):
        """Constructs all the scenarios"""
        scenarios = []
        scenarios_paths = []
        for test in sorted(os.listdir(self.set_path)):
            test_dir = os.path.join(self.set_path, test)
            if os.path.isdir(test_dir):
                if SCENARIO in os.listdir(test_dir):
                    scenario_path = os.path.join(test_dir, SCENARIO)
                    scenarios_paths.append(scenario_path)
        for scenario_path in scenarios_paths:
            scenario_parser = parser.Parser()
            scenario_stream = scenario_parser.parse_yaml(scenario_path)
            scenarios.append(scenario.Scenario(scenario_path, scenario_stream, self.controller))

        self.scenarios = scenarios

    def run(self):
        """Runs one or all tests in a set"""
        # TODO: handle this scenario resolution way earlier
        if os.path.basename(self.tests_to_run) != "All":
            # we are only interested in a particular scenario
            scenarios_to_run = [ s for s in self.scenarios if
                                os.path.basename(s.dirname) ==
                                os.path.basename(self.tests_to_run) ]
            if len(scenarios_to_run) != 1:
                raise Exception("too many/few scenarios")
        else:
            scenarios_to_run = self.scenarios
        # TODO: run init
        for scen in scenarios_to_run:
            scen.run()

        # cleanup networks
        for net in self.networks:
            net.destroy()

# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

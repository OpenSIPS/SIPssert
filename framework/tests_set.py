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
from framework import config
from framework import scenario
from framework import logger
from framework import tasks_parser
from framework.network import network

SCENARIO = "scenario.yml"
CONFIG = "config.yml"
VARIABLES = "defines.yml"

class TestSet():

    """Main class that runs a set of tests"""

    def __init__(self, set_path, controller, tests):
        self.controller = controller
        self.tests_to_run = tests
        self.name = os.path.basename(set_path)
        self.set_path = set_path
        self.set_logs_dir = controller.run_logs_dir + "/" + self.name
        self.config = config.Config(self.set_path, CONFIG, VARIABLES, controller.config.get_defines())
        self.create_set_logs_dir()
        self.defaults = self.config.get("defaults", {})
        self.init_tasks = tasks_parser.create_task_list("init_tasks",
                self.set_path, self.config, self.controller, self.defaults)
        self.cleanup_tasks = tasks_parser.create_task_list("cleanup_tasks",
                self.set_path, self.config, self.controller, self.defaults)
        self.setup_networks()
        self.build_scenarios()

    def create_set_logs_dir(self):
        """Creates current test set logs directory"""
        if not os.path.isdir(self.set_logs_dir):
            os.mkdir(self.set_logs_dir)

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
        nets = self.config.get("networks")
        self.networks = network.get_networks(self.controller, nets)

    def build_scenarios(self):
        """Constructs all the scenarios"""
        scenarios = []
        scenarios_paths = []
        for test in sorted(os.listdir(self.set_path)):
            if len(self.tests_to_run) != 0 and test not in self.tests_to_run:
                continue
            test_dir = os.path.join(self.set_path, test)
            if os.path.isdir(test_dir):
                if SCENARIO in os.listdir(test_dir):
                    scenario_path = os.path.join(test_dir, SCENARIO)
                    scenarios_paths.append(scenario_path)
        for scenario_path in scenarios_paths:
            scenarios.append(scenario.Scenario(scenario_path, self.controller, self, self.set_logs_dir, self.defaults))

        self.scenarios = scenarios

    def init(self):
        """Runs the init tasks for a test set"""
        for task in self.init_tasks:
            task.run()

    def cleanup(self):
        """Runs the cleanup tasks for a test set"""
        for task in self.cleanup_tasks:
            task.run()

    def run(self):
        """Runs one or all tests in a set"""
        try:
            self.init()
        except Exception as e:
            logger.slog.exception(e)
            return
        try:
            for scen in self.scenarios:
                scen.run()
        except Exception as e:
            logger.slog.exception(e)
        try:
            self.cleanup()
        except Exception as e:
            logger.slog.exception(e)
        # cleanup networks
        for net in self.networks:
            net.destroy()

# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

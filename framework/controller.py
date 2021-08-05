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
import docker
from framework import parser
from framework import scenario

class Controller:

    def __init__(self, tests_dir):
        self.tests_dir = tests_dir

        self.parser = parser.Parser(self.tests_dir)

        scenario_configs = self.parser.parse_scenario_configs()

        self.docker = docker.from_env()

        self.scenarios = []
        for f, cfg in scenario_configs:
            self.scenarios.append(scenario.Scenario(f, cfg, self))

        self.setup_network()

    def __del__(self):
        # destroy the network when the controller is done
        self.destroy_network()

    def destroy_network(self):
        try:
            self.docker.networks.get("controllerNetwork").remove()
        except docker.errors.APIError as err:
            if type(err) == docker.errors.NotFound:
                print("Network not found!")
            else:
                print("Something else went wrong!")
        except ValueError:
            pass
        finally:
            print("New network can be created!")

    def setup_network(self):

        # make sure we cleanup if there was any remaining network
        self.destroy_network()
        try:
            ipam_pool = docker.types.IPAMPool(subnet='192.168.52.0/24', gateway='192.168.52.254')
            ipam_config = docker.types.IPAMConfig(pool_configs=[ipam_pool])
            self.docker.networks.create("controllerNetwork", driver="bridge", ipam=ipam_config)
        except docker.errors.APIError as err:
            print(type(err))

    def run(self):
        for s in self.scenarios:
            s.run()
            s.wait_end()  #wait 10 secs (TODO this should come from scenario)

# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

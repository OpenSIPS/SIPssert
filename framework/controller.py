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

from time import sleep
import docker
from framework import parser
from framework import scenario
from datetime import datetime

class Controller:

    def __init__(self, sets_dir):
        self.sets_dirs = sets_dir
        self.sets_dict = {}

        self.parser = parser.Parser(self.sets_dirs)
        self.parser.get_sets()
        for set in self.parser.sets:
            scenarios = []
            set_scenarios = self.parser.parse_set_scenarios(set)
            for f, cfg in set_scenarios:
                scenarios.append(scenario.Scenario(f, cfg, self))
            self.sets_dict[set] = scenarios

        self.docker = docker.from_env()

    def __del__(self):
        # destroy the network when the controller is done
        # self.destroy_network()
        pass


    def check_network(self, network):
        try:
            self.docker.networks.get(network).remove()
        except docker.errors.APIError as err:
            if type(err) == docker.errors.NotFound:
                print(datetime.utcnow(), "- Network: {} can be created!".format(network))
            else:
                print(datetime.utcnow(), "- Something else went wrong!")

    def destroy_network(self, network):
        try:
            self.docker.networks.get(network).remove()
        except docker.errors.APIError as err:
            if type(err) == docker.errors.NotFound:
                print(datetime.utcnow(), "- Network: {} not found!".format(network))
            else:
                print(datetime.utcnow(), "- Something else went wrong!")
        finally:
            print(datetime.utcnow(), "- Network: {} succesfully deleted!".format(network))
        
    def setup_network(self, network, device):

        # make sure we cleanup if there was any remaining network
        self.check_network(network)
        if device != "host":
            try:
                ipam_pool = docker.types.IPAMPool(subnet='192.168.52.0/24', gateway='192.168.52.254')
                ipam_config = docker.types.IPAMConfig(pool_configs=[ipam_pool])
                self.docker.networks.create(network, driver="bridge", ipam=ipam_config, options={"com.docker.network.bridge.name":device})
            except docker.errors.APIError as err:
                print(type(err))
            finally:
                print(datetime.utcnow(), "- Network: {} successfully created!".format(network))
        elif device == "host":
            print("type = HOST!")
            pass

    def run(self):
        for set in self.sets_dict:
            print("="*35,set.getSetName(),"="*35 )
            for scenario in self.sets_dict[set]:
                network_name = "controllerNetwork"
                self.setup_network(network_name, scenario.network_device)
                scenario.start_tcpdump()
                scenario.run()
                scenario.wait_end()  #wait 10 secs (TODO this should come from scenario)
                scenario.stop_tcpdump()
                scenario.get_logs()
                scenario.get_status()
                scenario.verify_test()
                self.destroy_network(network_name)

# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

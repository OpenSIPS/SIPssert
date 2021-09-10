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
from framework.networks import bridged_network
from framework.networks import host_network
import os

SCENARIO = "scenario.yml"
CONFIG = "config.yml"

class TestSet():
    def __init__(self, set_path, controller):
        self.name = os.path.basename(set_path)
        self.set_path = set_path
        self.controller = controller
        self.config = None
        self.scenarios = None
        self.networks = []
        self.set_type = None

    def getSetName(self):
        return self.name

    def getSetPath(self):
        return self.set_path
    
    def getSetScenarios(self):
        return self.scenarios

    def getSetNetworks(self):
        return self.networks

    def hasConfig(self):
        if self.config:
            return True
        else:
            return False

    def getSetConfig(self):
        return self.config

    def hasNetworksConfig(self):
        if self.hasConfig():
            if "networks" in self.config.keys():
                return True
        
        return False

    def getNetworkConfig(self):
        return self.config["networks"]        

    def setNetworks(self):
        networks = []
        if self.hasNetworksConfig():
            networks_stream = self.getNetworkConfig()
            for n in networks_stream:
                net = bridged_network.BridgedNetwork(n)
                networks.append(net)

        self.networks = networks

    def setConfig(self):
        if CONFIG in os.listdir(self.set_path):
            p = parser.Parser()
            config_stream = p.parse_yaml(os.path.join(self.set_path, CONFIG))
            self.config = config_stream
        else:
            self.config = None

        if self.hasNetworksConfig():
            self.set_type = "bridge"
        else:
            self.set_type = "host"

    def findNetwork(self, name):
        for n in self.getSetNetworks():
            if n.getName() == name:
                return n
        
        return None

    def getScenarioNetwork(self, scenario):
        # TODO get network from a scenario
        # return scenario.getNetwork()
        network_name = scenario.getNetwork()
        network = self.findNetwork(network_name)
        return network

    def getScenariosPaths(self):
        scenarios_paths = []
        for test in os.listdir(self.set_path):
            test_dir = os.path.join(self.set_path, test)
            if os.path.isdir(test_dir):
                if SCENARIO in os.listdir(test_dir):
                    scenario_path = os.path.join(test_dir, SCENARIO)
                    scenarios_paths.append(scenario_path)
        
        return scenarios_paths

    def setScenarios(self):
        scenarios = []
        scenarios_paths = self.getScenariosPaths()
        for scenario_path in scenarios_paths:
            p = parser.Parser()
            scenario_stream = p.parse_yaml(scenario_path)
            scenarios.append(scenario.Scenario(scenario_path, scenario_stream, self.controller))

        self.scenarios = scenarios

    def getSetType(self):
        return self.set_type

    def run(self):
        self.setConfig()
        self.setNetworks()
        if self.getSetType() == "bridge":
            self.setScenarios()
            for s in self.getSetScenarios():
                network = self.getScenarioNetwork(s)
                self.setupBridgeNetwork(network)
                s.startTcpdump()
                s.run()
                s.waitEnd()  #wait 10 secs (TODO this should come from scenario)
                s.stopTcpdump()
                s.getLogs()
                s.getStatus()
                s.verifyTest()
                self.destroyNetwork(network)
        elif self.getSetType() == "host":
            self.setScenarios()
            for s in self.getSetScenarios():
                s.startTcpdump()
                s.run()
                s.waitEnd()  #wait 10 secs (TODO this should come from scenario)
                s.stopTcpdump()
                s.getLogs()
                s.getStatus()
                s.verifyTest()


    def checkNetwork(self, network):
        name = network.getName()
        try:
            self.controller.docker.networks.get(name).remove()
        except docker.errors.APIError as err:
            if type(err) == docker.errors.NotFound:
                print(datetime.utcnow(), "- Network: {} can be created!".format(name))
            else:
                print(datetime.utcnow(), "- Something else went wrong!")

    def destroyNetwork(self, network):
        name = network.getName()
        try:
            self.controller.docker.networks.get(name).remove()
        except docker.errors.APIError as err:
            if type(err) == docker.errors.NotFound:
                print(datetime.utcnow(), "- Network: {} not found!".format(name))
            else:
                print(datetime.utcnow(), "- Something else went wrong!")
        finally:
            print(datetime.utcnow(), "- Network: {} succesfully deleted!".format(name))
        
    def setupBridgeNetwork(self, network):
        name = network.getName()
        subnet = network.getSubnet()
        gateway = network.getGateway()
        device = network.getDevice()
        driver = "bridge"

        # make sure we cleanup if there was any remaining network
        self.checkNetwork(network)
        try:
            ipam_pool = docker.types.IPAMPool(subnet=subnet, gateway=gateway)
            ipam_config = docker.types.IPAMConfig(pool_configs=[ipam_pool])
            self.controller.docker.networks.create(name, driver=driver, ipam=ipam_config, options={"com.docker.network.bridge.name":device})
        except docker.errors.APIError as err:
            print(type(err))
        finally:
            print(datetime.utcnow(), "- Network: {} successfully created!".format(name))

# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

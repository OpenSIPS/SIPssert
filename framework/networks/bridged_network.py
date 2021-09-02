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

from framework.networks.network import Network

class BridgedNetwork(Network):
    # TODO bridge network configuration
    def __init__(self, network_config):
        self.type = "bridge"
        self.name = network_config["name"]
        self.subnet = network_config["subnet"]
        self.gateway = network_config["gateway"]

        if "device" in network_config.keys():
            self.device = network_config["device"]
        else:
            self.device = network_config["name"]

    def isHost(self):
        return False

    def getName(self):
        return self.name

    def getSubnet(self):
        return self.subnet

    def getGateway(self):
        return self.gateway

    def getDevice(self):
        return self.device


# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

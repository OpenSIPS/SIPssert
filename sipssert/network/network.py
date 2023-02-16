#!/usr/bin/env python
##
## This file is part of the SIPssert Testing Framework project
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

"""Abstract class that defines the required fields for a network type"""

from abc import ABC, abstractmethod
import sipssert.network

class NetworkError(Exception):
    """Generic Network Exception"""

class NetworkBadConfig(NetworkError):
    """Exception raised for bad configuration"""

class Network(ABC):

    """Abstract class for Network"""

    net_type = "unknown"
    name = "unknown"

    @abstractmethod
    def setup(self):
        """Sets up the network"""

    @abstractmethod
    def destroy(self):
        """Destroys the network"""

def get_networks(controller, config):
    """Parses tests sets configuration"""

    # TODO: rearange networks as key-values in YAML

    # "host" network is always available
    if not config:
        return [sipssert.network.DefaultNetwork()]

    networks = []
    # check if they have same name, or host name
    try:
        names = [ n["name"] for n in config ]
    except KeyError as exc:
        raise NetworkBadConfig("network without name") from exc
    # check if host is re-defined
    if "host" in names:
        raise NetworkBadConfig("'host' network name is not allowed")
    if len(names) != len(set(names)):
        # duplicate names
        for name in names:
            if len([ x for x in names if x == name ]) > 1:
                raise NetworkBadConfig(f"duplicate network name {name}")
    for net in config:
        net_type = "bridged" if "type" not in net else net["type"]
        if net_type == "bridged":
            network = sipssert.network.BridgedNetwork(controller, net)
        elif net_type == "host":
            network = sipssert.network.HostNetwork(net)
        else:
            raise NetworkBadConfig(f"unknown type {net_type}")
        networks.append(network)

    return networks

# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

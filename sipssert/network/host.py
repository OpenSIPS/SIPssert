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

"""Implementation of the Host Network adapter"""

from sipssert.network import network

class HostNetwork(network.Network):

    """Host Network adapter"""

    def __init__(self, config):
        self.net_type = "host"
        self.name = config["name"]

    def setup(self):
        """Sets up the network"""

    def destroy(self):
        """Destroys the network"""

class DefaultNetwork(HostNetwork):

    """Default Host Network"""

    def __init__(self):
        super().__init__({"name":"host"})

# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

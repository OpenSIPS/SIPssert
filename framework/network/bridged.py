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


"""Implementation of the brided network type"""

import docker
from framework.network import network
from framework import logger

class BridgedNetworkBadConfig(network.NetworkBadConfig): # pylint: disable=too-few-public-methods
    """Invalid config for Bridged Network"""

class BridgedNetworkOperation(network.NetworkError): # pylint: disable=too-few-public-methods
    """Operations error for Bridged Network"""

class BridgedNetwork(network.Network):
    """Bridged Network adapter"""

    net_type = "bridged"

    """Implemention about of the 'bridged' network type"""

    def __init__(self, controller, network_config):

        try:
            self.controller = controller
            self.name = network_config["name"]
            self.subnet = network_config["subnet"]
            self.gateway = network_config["gateway"]
            self.created = False
        except KeyError as exc:
            raise BridgedNetworkBadConfig("invalid setting") from exc

        if "device" in network_config.keys():
            self.device = network_config["device"]
        else:
            self.device = self.name
        self.setup()

    def setup(self):
        """Sets up the network"""
        try:
            ipam_pool = docker.types.IPAMPool(subnet=self.subnet,
                                              gateway=self.gateway)
            ipam_config = docker.types.IPAMConfig(pool_configs=[ipam_pool])
            options = {
                    "com.docker.network.bridge.name": self.device
                    }

            self.controller.docker.networks.create(self.name,
                                                   driver="bridge",
                                                   ipam=ipam_config,
                                                   options=options)
            self.created = True
        except docker.errors.APIError as err:
            raise BridgedNetworkOperation(f"cannot create bridged adapter {self.name}") from err
        finally:
            logger.slog.info("bridged adapter %s successfully created!", self.name)


    def destroy(self):
        """Destroys the network"""
        if not self.created:
            return
        try:
            self.controller.docker.networks.get(self.name).remove()
            self.created = False
            logger.slog.debug("bridged adapter %s destroyed!", self.name)
        except docker.errors.NotFound:
            logger.slog.debug("bridged adapter %s not found!", self.name)
            self.created = False
        except docker.errors.APIError:
            logger.slog.exception("could not remove adapter %s!", self.name)

    def __del__(self):
        """Deletes the network in case destroy is missed"""
        self.destroy()

# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

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

import docker
from framework import parser

class Controller:

    def __init__(self, tests_dir):
        self.tests_dir = tests_dir

        self.parser = parser.Parser(self.tests_dir)

        self.scenarios = self.parser.parse_scenarios()

        self.docker = docker.from_env()

        self.setup_network()

        # TODO: fix this
        entities = []
        for scenario in self.scenarios:
            self.parser.streamToEntities(scenario, entities)

        for e in entities:
            if e.type == "uas-sipp":
                params = "-sn uas" + e.getExtraParams()
                e.ports = self.parser.setPorts(e.ports)
                container = self.docker.containers.run(e.image, params, detach=True, ports = e.ports)
            elif e.type == "opensips":
                mount_point = e.getMountPoint()
                path_config = os.path.abspath(e.getPathConfig())
                params = "-f " + mount_point + e.getConfigFile()
                print(path_config)
                print(mount_point)
                print(params)
                e.ports = self.parser.setPorts(e.ports)
                container = self.docker.containers.create(e.image, params, detach=True,
                volumes={path_config:{'bind':mount_point, 'mode':'ro'}},
                ports = e.ports)
                self.docker.networks.get("controllerNetwork").connect(container, ipv4_address=e.ip)
                
                container.start()

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

# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

#!/usr/bin/env python
##
## TODO: update project's name
## (see https://github.com/OpenSIPS/opensips-cli).
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

class Entity():
    def __init__(self, name, type, image, ports, ip):
        self.name = name
        self.type = type
        self.image = image
        self.ports = ports
        self.ip = ip

    def getName(self):
        return self.name

    def getType(self):
        return self.type

    def getImage(self):
        return self.image

    def getPorts(self):
        return self.ports

    def getIp(self):
        return self.ip


class Entity_uas(Entity):
    def setExtraParams(self, extra_params):
        self.extra_params = extra_params

    def getExtraParams(self):
        return self.extra_params

class Entity_uac(Entity):
    def setExtraParams(self, extra_params):
        self.extra_params = extra_params

    def getExtraParams(self):
        return self.extra_params

class Entity_opensips(Entity):

    def setExtraParams(self, extra_params):
        self.extra_params = extra_params

    def getExtraParams(self):
        return self.extra_params

    def setPathConfig(self, path_cfg):
        self.path_cfg = path_cfg

    def getPathConfig(self):
        return self.path_cfg

    def setMountPoint(self, mount_point):
        self.mount_point = mount_point

    def getMountPoint(self):
        return self.mount_point

    def setConfigFile(self, file):
        self.config_file = file

    def getConfigFile(self):
        return self.config_file

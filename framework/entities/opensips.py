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
from framework.entities.entity import Entity

class OpenSIPSEntity(Entity):

    entity_default_mount_point = "/etc/opensips"
    entity_default_image = "opensips/opensips"

    def __init__(self, test_dir, config, controller):

        Entity.__init__(self, test_dir, config, controller)

        if "config_file" in self.config:
            self.config_file = self.config["config_file"]
        else:
            self.config_file = None

    def get_entity_args(self):

        args = []

        # handle config
        if self.config_file:
            # if an absolute path, leave it as it is
            if os.path.isabs(self.config_file):
                cfg = self.config_file
            else:
                # path is relative to the mount point
                cfg = os.path.join(self.get_mount_point(), self.config_file)
            args.append("-f")
            args.append(cfg)

        return args

# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

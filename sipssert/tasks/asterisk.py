#!/usr/bin/env python
##
## This file is part of the SIPssert Testing Framework project
## Copyright (C) 2023 OpenSIPS Solutions
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
from sipssert.task import Task

class AsteriskTask(Task):

    default_image = "yaroslavonline/asterisk"
    default_mount_point = "/home"
    default_daemon = True

    asterisk_config_dir = "/etc/asterisk"

    def __init__(self, test_dir, config):
        super().__init__(test_dir, config)

        self.config_files = config.get("config_files")
        if self.config_files and isinstance(self.config_files, list):
            for item in self.config_files:
                files = item.split(":") 
                if len(files) == 2:
                    self.add_volume_dir(os.path.join(test_dir, files[1]),
                        dest=os.path.join(self.asterisk_config_dir, files[0]))

# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

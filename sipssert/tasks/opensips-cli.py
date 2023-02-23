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

class OpenSIPSCliTask(Task):

    default_image = "opensips/opensips-cli"
    default_mount_point = "/home"
    default_daemon = False

    default_port = 8888
    default_ip = '127.0.0.1'
    default_path = 'mi'

    def __init__(self, test_dir, config):
        super().__init__(test_dir, config)
        self.script = config.get("script")

        if self.script and not os.path.isabs(self.script):
            self.script = os.path.join(self.mount_point, self.script)
    
    def get_task_args(self):

        args = []

        # handle config
        if self.config_file:
            args.append("-f")
            args.append(self.config_file)

        ip = self.config.get("mi_ip", self.default_ip)
        port = self.config.get("mi_port", self.default_port)
        path = self.config.get("mi_path", self.default_path)
        args.append("-o")
        args.append(f"url=http://{ip}:{port}/{path}")

        if self.script:
            args.append(self.script)

        return args

# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

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

class OpenSIPSMITask(Task):

    default_image = "opensips/python-opensips"
    default_mount_point = "/home"
    default_daemon = False

    default_port = 8888
    default_ip = '127.0.0.1'
    default_comm_type = 'http'

    def __init__(self, test_dir, config):
        super().__init__(test_dir, config)
        self.script = config.get("script")

        if self.script and not os.path.isabs(self.script):
            self.script = os.path.join(self.mount_point, self.script)

    def get_task_env(self):
        env_dict = super().get_task_env()
        env_dict["MI_TYPE"] = self.config.get("mi_type", self.default_comm_type)
        self.mi_type = env_dict["MI_TYPE"]
        env_dict["MI_IP"] = self.config.get("mi_ip", self.default_ip)
        self.mi_ip = env_dict["MI_IP"]
        env_dict["MI_PORT"] = self.config.get("mi_port", self.default_port)
        self.mi_port = env_dict["MI_PORT"]
        return env_dict
    
    def get_task_args(self):

        args = []

        if self.script:
            args.append(self.script)
        else:
            self.mi_type = self.config.get("mi_type", self.default_comm_type)
            self.mi_ip = self.config.get("mi_ip", self.default_ip)
            self.mi_port = self.config.get("mi_port", self.default_port)
            args.append("-t")
            args.append(self.mi_type)
            args.append("-i")
            args.append(self.mi_ip)
            args.append("-p")
            args.append(str(self.mi_port))

        return args

# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

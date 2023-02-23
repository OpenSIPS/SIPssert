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

"""Generic SIPP User-Agent class"""

import os
from sipssert import logger
from sipssert.task import Task

SCENARIO_NAME = "sipp.xml"

class SIPPTask(Task):

    """Generic SIPP class"""

    default_image = "ctaloi/sipp"
    default_daemon = False

    def __init__(self, test_dir, config):
        super().__init__(test_dir, config)

        self.username = config.get("username")
        self.password = config.get("password")
        self.port = config.get("port", None)
        self.keys = config.get("keys", {})
        self.calls = config.get("calls", "1")
        self.duration = str(config.get("duration", "5000"))
        self.proxy = config.get("proxy", None)
        self.service = config.get("service", None)

        if not self.config_file:
            scenario = os.path.join(self.test_dir, SCENARIO_NAME)
            if os.path.exists(scenario):
                self.config_file = os.path.join(self.mount_point, SCENARIO_NAME)

    def get_task_args(self):

        """Returns the arguments the container uses to start"""

        args = []

        # handle config
        if self.config_file:
            args.append("-sf")
            args.append(self.config_file)

        if self.username:
            args.append("-au")
            args.append(self.username)

        if self.password:
            args.append("-ap")
            args.append(self.password)

        if self.service:
            args.append("-s")
            args.append(self.service)

        if self.port:
            args.append("-p")
            args.append(str(self.port))

        if self.ip:
            args.append("-i")
            args.append(self.ip)

        for k, v in self.keys.items():
            args.append("-key")
            args.append(str(k))
            args.append(str(v))

        if self.calls != "unlimited":
            args.append("-m")
            args.append(str(self.calls))

        if self.duration != "0":
            args.append("-d")
            args.append(self.duration)

        if self.proxy:
            args.append(self.proxy)

        return args

# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

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

class AmiClientTask(Task):

    default_image = "yaroslavonline/ami-client"
    default_mount_point = '/home'
    default_daemon = True

    def __init__(self, test_dir, config):
        super().__init__(test_dir, config)
        self.script = config.get("script")

        self.asterisk_ip = self.config.get("asterisk_ip")
        self.login = self.config.get("login")
        self.secret = self.config.get("secret")

        if self.script and not os.path.isabs(self.script):
            self.script = os.path.join(self.mount_point, self.script)

    def get_task_args(self):
        args = []

        if self.script:
            args.append(self.script)
        else:
            if self.config_file:
                args.append("--config")
                args.append(self.config_file)

            if self.asterisk_ip:
                args.append("--asteriskip")
                args.append(self.asterisk_ip)

            if self.login:
                args.append("--login")
                args.append(self.login)

            if self.secret:
                args.append("--secret")
                args.append(self.secret)

        return args

# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

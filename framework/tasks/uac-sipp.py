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

from framework.tasks.task import Task

class UacSIPPTask(Task):

    default_image = "ctaloi/sipp"
    default_daemon = False

    def __init__(self, test_dir, config, controller):
        super().__init__(test_dir, config, controller)

        self.username = config.get("username")
        self.password = config.get("password")
        self.proxy = config["proxy"]

    def get_task_args(self):

        args = []

        # handle config
        if self.config_file:
            args.append("-sf")
            args.append(self.config_file)
        else:
            args.append("-sn")
            args.append("uac")

        if self.username:
            args.append("-s")
            args.append(self.username)

        if self.password:
            args.append("-ap")
            args.append(self.password)

        return args

# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

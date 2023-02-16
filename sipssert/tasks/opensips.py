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

from sipssert.tasks.task import Task

class OpenSIPSTask(Task):

    default_mount_point = "/etc/opensips"
    default_image = "opensips/opensips"
    default_daemon = True
    
    def get_task_args(self):

        args = []

        # handle config
        if self.config_file:
            args.append("-f")
            args.append(self.config_file)

        return args

# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

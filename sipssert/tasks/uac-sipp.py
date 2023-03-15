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

"""SIPP User-Agent Client class"""

from sipssert.tasks.sipp import SIPPTask

class UacSIPPTask(SIPPTask):

    """UAC SIPP class"""
    def __init__(self, test_dir, config):
        super().__init__(test_dir, config)
        self.remote = config.get("remote")
        if not self.remote and not self.proxy:
            raise ConfigParamNotFound("proxy")
        if not self.proxy:
            self.proxy = self.remote
            self.remote = None
        elif self.remote:
            # we have both - swap them
            tmp = self.remote
            self.remote = self.proxy
            self.proxy = tmp
        self.caller = config.get("caller", self.username)
        # overwrite the username/service with the destination 
        if not self.service:
            self.service = config.get("destination", self.username)

    def get_task_args(self):

        """Returns the arguments the container uses to start"""

        args = super().get_task_args()
        if not self.config_file:
            args.append("-sn")
            args.append("uac")
        if self.caller:
            args.append("-key")
            args.append("caller")
            args.append(self.caller)
        if self.remote:
            args.append("-rsa")
            args.append(self.remote)

        return args

# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

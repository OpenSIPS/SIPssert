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

"""Sleep runner class"""

import os
from sipssert import logger
from sipssert.task import Task

class SleepTask(Task):

    """Sleep class"""

    default_image = "debian"

    def __init__(self, test_dir, config):

        super().__init__(test_dir, config)
        self.seconds = config.get("seconds", 0)
        self.milliseconds = config.get("milliseconds", 0) / 1000
        if self.seconds > self.milliseconds:
            self.timeout = self.milliseconds
        else:
            self.timeout = self.seconds

    def get_task_args(self):
        return [ "sleep", str(self.timeout) ]

# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

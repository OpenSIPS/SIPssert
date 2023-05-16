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

    asterisk_modules_conf = "/etc/asterisk/modules.conf"
    asterisk_pjsip_conf = "/etc/asterisk/pjsip.conf"
    asterisk_extensions_conf = "/etc/asterisk/extensions.conf"
    asterisk_extensions_lua = "/etc/asterisk/extensions.lua"
    asterisk_logger_conf = "/etc/asterisk/logger.conf"

    def __init__(self, test_dir, config):
        super().__init__(test_dir, config)

        self.config = config.get("config")
        self.modules_file = self.config.get("modules") if isinstance(self.config, dict) else None
        self.pjsip_file = self.config.get("pjsip") if isinstance(self.config, dict) else None
        self.logger_file = self.config.get("logger") if isinstance(self.config, dict) else None

        if self.modules_file:
            self.add_volume_dir(os.path.join(test_dir, self.modules_file),
                dest=self.asterisk_modules_conf)

        if self.pjsip_file:
            self.add_volume_dir(os.path.join(test_dir, self.pjsip_file),
                dest=self.asterisk_pjsip_conf)
    
        if self.logger_file:
            self.add_volume_dir(os.path.join(test_dir, self.logger_file),
                dest=self.asterisk_logger_conf)
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

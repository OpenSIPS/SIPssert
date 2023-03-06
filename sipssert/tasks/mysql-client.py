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

from sipssert.task import Task

class MysqlClientTask(Task):

    mysql_default_env = {}
    default_image = "opensips/mysql-client"

    def get_task_env(self):

        env_dict = {}

        if "user" in self.config:
            self.user = self.config["user"]
            env_dict["MYSQL_user"] = self.user

        if "password" in self.config:
            self.password = self.config["password"]
            env_dict["MYSQL_PASSWORD"] = self.password

        if "host" in self.config:
            self.password = self.config["host"]
            env_dict["MYSQL_HOST"] = self.host

        if "port" in self.config:
            self.port = self.config["port"]
            env_dict["MYSQL_PORT"] = self.host

        if "database" in self.config:
            self.database = self.config["database"]
            env_dict["MYSQL_DATABASE"] = self.database

        if "options" in self.config:
            self.options = self.config["options"]
            self.mysql_options = ""
            for k, v in self.options:
                self.mysql_options += "{} = {}\r\n".format(k, v)

            env_dict["MYSQL_OPTIONS"] = self.mysql_options

        return env_dict

# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

#!/usr/bin/env python
##
## This file is part of the SIPssert Testing Framework project
## Copyright (C) 2026 OpenSIPS Solutions
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

"""RTPengine runner class"""

import shlex

from sipssert.task import Task


class RTPEngineTask(Task):

    """RTPengine class"""

    default_daemon = True
    default_stop_timeout = 3
    default_image = "debian:trixie-slim"

    def __init__(self, test_dir, config):

        super().__init__(test_dir, config)
        self.entrypoint = config.get("entrypoint", "sh")

        self.ip = config.get("ip", "127.0.0.1")
        # `ng_port` is the rtpengine control (ng) port. Note we deliberately do
        # NOT alias the base `port`/`ports` keys here: those are reserved by the
        # base Task for container port *publishing* and a string value there
        # (e.g. "22222") would crash get_ports(); the ng port is reached over
        # the scenario bridge and never published.
        self.ng_port = config.get("ng_port", "22222")
        self.interface = config.get("interface", self.ip)
        self.table = config.get("table", "-1")
        self.install = config.get("install", True)
        self.packages = self.normalize_list(config.get("packages", [
            "rtpengine-daemon",
            "iproute2",
        ]))
        self.options = config.get("options", [])

        if "healthcheck" not in config:
            self.healthcheck = {
                "test": f"ss -lnu | grep -q :{self.ng_port}",
                "interval": 2000000000,
                "timeout": 2000000000,
                "retries": 120,
            }

    def get_task_args(self):
        return [
            "-c",
            " && ".join(self.get_setup_commands() + [self.get_run_command()]),
        ]

    def get_setup_commands(self):
        if not self.install:
            return []

        packages = " ".join(shlex.quote(str(pkg)) for pkg in self.packages)
        return [
            "echo 'exit 101' > /usr/sbin/policy-rc.d",
            "chmod +x /usr/sbin/policy-rc.d",
            "apt-get update",
            "DEBIAN_FRONTEND=noninteractive apt-get install -y "
            f"--no-install-recommends {packages}",
        ]

    def get_run_command(self):
        args = [
            "exec",
            "rtpengine",
            "--table=" + str(self.table),
            "--interface=" + str(self.interface),
            "--listen-ng=" + str(self.ip) + ":" + str(self.ng_port),
            "--foreground",
            "--log-stderr",
        ]
        args += self.normalize_options(self.options)
        return " ".join(shlex.quote(str(arg)) for arg in args)

    def normalize_options(self, options):
        return self.normalize_list(options)

    def normalize_list(self, options):
        if options is None:
            return []
        if isinstance(options, str):
            return shlex.split(options)
        return [str(option) for option in options]


# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

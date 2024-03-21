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

"""
Implements an object that captures network communication
"""

import os
import time
import subprocess
from sipssert import logger

class Tracer():

    """Class that implements the network capturing"""

    def __init__(self, directory, filename, net=[], name=None):
        # TODO: use tshark instead of tcpdump
        if len(net) == 0 or (len(net) == 1 and net == "host") or len(net) > 1:
            self.interface = "any"
        else:
            self.interface = net[0]
        self.name = name if name else filename
        self.capture_file = os.path.join(directory, f"{filename}.pcap")
        self.process = None

    def status(self):
        if not self.process:
            return None, None
        rc = self.process.returncode
        if rc and rc != 0:
            ret = self.process.communicate()[1]
            if ret:
                ret = ret.decode('utf-8')
        else:
            ret = None
        return rc, ret

    def stop(self):
        """Stops started tcpdump"""
        if not self.process:
            return
        self.process.terminate()
        self.process.wait()
        rc, err = self.status()
        self.process = None
        logger.slog.debug(f"stopped tracer for {self.name}")
        if rc and rc != 0:
            logger.slog.error(f"tracer {self.name} failed with ({rc}):\n{err}")

    def start(self):
        """Starts a tcpdump for a scenario"""
        self.process = subprocess.Popen(['tcpdump',
            '-i', self.interface,
            '-w', self.capture_file],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE)
        rc, err = self.status()
        if rc and rc != 0:
            logger.slog.error(f"could not start tracer {self.name} ({rc}):\n{err}")
            # wait for proc to start
        else:
            logger.slog.debug(f"started tracer for {self.name}")
            time.sleep(0.5)


# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

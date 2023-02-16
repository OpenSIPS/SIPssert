#!/usr/bin/env python
##
## This file is part of the SIPssert Testing Framework project
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

class Tracer():

    """Class that implements the network capturing"""

    def __init__(self, directory, name, net=None):
        self.interface = "any" if not net or net == "host" else net
        self.capture_file = os.path.join(directory, f"{name}.pcap")
        self.process = None

    def stop(self):
        """Stops started tcpdump"""
        if not self.process:
            return
        self.process.terminate()
        self.process.wait()
        self.process = None

    def start(self):
        """Starts a tcpdump for a scenario"""
        self.process = subprocess.Popen(['tcpdump',
            '-i', self.interface,
            '-w', self.capture_file],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL)
        # wait for proc to start
        time.sleep(0.5)


# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

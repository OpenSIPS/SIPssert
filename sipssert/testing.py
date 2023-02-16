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
Object that implements the testing logging
"""
import os
from enum import Enum

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

class TestStatus(Enum):
    UNKN, PASS, FAIL, TOUT = range(4)

    def __str__(self):
        return super().__str__()[len(self.__class__.__name__) + 1:]

    def __repr__(self):
        return self.__str__()

    def __len__(self):
        return len(str(self))

    def __lt__(self, other):
        if self.__class__ is other.__class__:
            return self.value < other.value
        return NotImplemented

statuses = {
        TestStatus.UNKN: bcolors.WARNING,
        TestStatus.PASS: bcolors.OKGREEN,
        TestStatus.FAIL: bcolors.FAIL,
        TestStatus.TOUT: bcolors.FAIL,
}

class Testing:
    """Class that implements the SIPssert Testing Framework"""

    def emit(self, message, end='\n'):
        """emits a message to output"""
        print(message, end=end)
    
    def emit_header(self, header):
        """emits testing header"""
        if len(header) > self.tab_size:
            header = header[0:self.tab_size]
        self.emit((" " + header + " ").center(self.tab_size, "="))

    def emit_status(self, status, status_color=None, reason=None):
        """emits a color status message with reason"""
        #length of colors is added to compensate that padding counts it as a visible character
        self.emit((f"{status_color + status + bcolors.ENDC}").rjust(self.max_status_len + 
            len(status_color + bcolors.ENDC), "."), "" if reason else "\n")
        if reason:
            self.emit(f" - {reason}")

    def test_set(self, header):
        """prints the header of a test set"""
        if len(header) > self.tab_size:
            header = header[0:self.tab_size]
        self.emit((" " + header + " ").center(self.tab_size, "="))

    def test_start(self, header):
        """prints the header of a test set"""
        #allow 3 characters of padding between test name and test status
        if len(header) > self.test_name_avail - 3:
            header = header[0:(self.test_name_avail - 3)]
        self.emit(header.ljust(self.test_name_avail, "."), "")

    def success(self, reason=None):
        """indicates a specific test has finished with success
            if test is not defined, the last test is considered"""
        self.status(TestStatus.PASS, reason)

    def failed(self, reason=None):
        """indicates that a test has finished with failure
            if test is not defined, the last test is considered"""
        self.status(TestStatus.FAIL, reason)

    def status(self, status, reason=None):
        """indicates the test has finished with a custom status
            if test is not defined, the last test is considered"""
        if status == TestStatus.PASS:
            self.success_no += 1
        else:
            self.failed_no += 1
        self.emit_status(str(status), statuses[status], reason)

    def end(self):
        """Finishes the testing process and writes a summary"""
        summary_name = "Summary: "
        self.emit(summary_name, "")
        self.emit(("Total").ljust((self.summary_size - len(summary_name)) // 3, " "), "")
        self.emit(("Passed").ljust((self.summary_size - len(summary_name)) // 3, " "), "")
        self.emit(("Failed").ljust((self.summary_size - len(summary_name)) // 3, " "))

        self.emit(" " * len(summary_name), "")
        self.emit((f"{self.success_no + self.failed_no}").ljust((self.summary_size - len(summary_name)) // 3, " "), "")
        self.emit((f"{self.success_no}").ljust((self.summary_size - len(summary_name))// 3, " "), "")
        self.emit((f"{self.failed_no}").ljust((self.summary_size - len(summary_name))// 3, " "))

    def __init__(self, header):
        self.tab_size = min(50, os.get_terminal_size().columns)
        self.summary_size = min(40, os.get_terminal_size().columns)
        self.max_status_len = 0
        for status_name in statuses:
            if len(status_name) > self.max_status_len:
                self.max_status_len = len(statuses[status_name])
        #available space for a test header to allow its status to fit in the table
        self.test_name_avail = self.tab_size - self.max_status_len
        self.success_no = 0
        self.failed_no = 0
        self.emit_header(header)

# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

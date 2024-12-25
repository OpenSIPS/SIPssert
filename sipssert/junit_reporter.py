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
junit_reporter.py - generates junit-xml compatible report
"""

from junit_xml import TestSuite, TestCase
from sipssert.testing import TestStatus

class JUnitReporter():

    """Class that generates junit-xml compatible report"""

    def __init__(self, name):
        self.name = name
        self.test_suites = []

    def __get_test_suite(self, name):
        for test_suite in self.test_suites:
            if test_suite.name == name:
                return test_suite
        return None

    def __get_test_case(self, test_suite_name, name):
        test_suite = self.__get_test_suite(test_suite_name)
        if test_suite is None:
            return None
        for test_case in test_suite.test_cases:
            if test_case.name == name:
                return test_case
        return None

    def __add_test_suite(self, name):
        test_suite = TestSuite(name, [])
        self.test_suites.append(test_suite)
        return test_suite

    def __add_test_case(self, test_suite_name, name):
        test_case = TestCase(name, classname=test_suite_name)
        test_suite = self.__get_test_suite(test_suite_name)

        if test_suite is None:
            test_suite = self.__add_test_suite(test_suite_name)

        test_suite.test_cases.append(test_case)
        return test_case

    def add_status(self, test_suite_name, name, status, elapsed_sec=0):
        test_case = self.__get_test_case(test_suite_name, name) 
        if test_case is None:
            test_case = self.__add_test_case(test_suite_name, name)

        if status == TestStatus.UNKN:
            test_case.add_error_info(message="Unknown")
        if status == TestStatus.FAIL:
            test_case.add_failure_info(message="Failure")
        if status == TestStatus.TOUT:
            test_case.add_failure_info(message="Timeout")
        if status == TestStatus.PASS:
            pass

        test_case.elapsed_sec = elapsed_sec

    def skip_test_case(self, test_suite_name, name):
        test_case = self.__get_test_case(test_suite_name, name) 
        if test_case is None:
            test_case = self.__add_test_case(test_suite_name, name)

        test_case.add_skipped_info(message="Filtered")

    def save_report(self, file_name="report.xml"):
        with open(file_name, 'w') as f:
            TestSuite.to_file(f, self.test_suites)

# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

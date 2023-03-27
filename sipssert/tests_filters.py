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

"""Implements the logic to parse and apply tests filters"""

import os
import fnmatch

class TestsFilter:

    """Class that implements the filters matching"""

    tests_set_pattern = None
    tests_pattern = None

    def __init__(self, definition = None):
        if not definition:
            return
        s = os.path.split(definition)
        if len(s) == 1:
            self.tests_pattern = definition
        elif len(s) == 2:
            self.tests_set_pattern = s[0]
            self.tests_pattern = s[1]

    def match(self, set_name, test_name):
        if self.tests_set_pattern and not fnmatch.fnmatch(set_name, self.tests_set_pattern):
            return False
        if self.tests_pattern and not fnmatch.fnmatch(test_name, self.tests_pattern):
            return False
        return True

def ParseTestsFilters(definitions):

    ret = []

    for definition in definitions:
        ret.append(TestsFilter(definition))

    return ret

def MatchTestsFilters(set_name, test_name, definition):

    for tests_filter in definition:
        if tests_filter.match(set_name, test_name):
            return True
    return False

def CanExecute(set_name, test_name, definitions):
    include, exclude = definitions

    ret = MatchTestsFilters(set_name, test_name, include) if include else True
    if ret and exclude and MatchTestsFilters(set_name, test_name, exclude):
        return False
    return ret

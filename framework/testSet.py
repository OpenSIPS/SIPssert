#!/usr/bin/env python
##
## TODO: update project's name
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


class TestSet():
    def __init__(self, set_name, scenarios):
        self.name = set_name
        self.scenarios = scenarios

    def getSetName(self):
        return self.name
    
    def getSetScenarios(self):
        return self.scenarios

# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

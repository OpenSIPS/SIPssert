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

import os
import importlib
from framework.entities import entity

class Scenario():

    def __init__(self, file, config, controller):

        self.controller = controller
        self.config = config
        self.file = file
        self.entities = []
        self.nondaemons = 0
        for e in config["entities"]:
            if "type" in e.keys():
                entity_type = e["type"].lower()
            else:
                # create a generic entity
                entity_type = ""

            new_entity = None
            try:
                entity_mod = getattr(
                        importlib.import_module("framework.entities"),
                        entity_type)
                normalized_entity_type = "".join(
                        [ x for x in entity_type if x.isalnum() ])
                normalized_class_name = normalized_entity_type + "entity"
                classes = [ c for c in dir(entity_mod) if
                        c.lower() == normalized_class_name and
                        c.endswith("Entity") ]
                if len(classes) == 0:
                    print("unknown entity derived from {}".
                            format(entity_type))
                elif len(classes) != 1:
                    print("too many classed derived from {}: {}".
                            format(entity_type, str(classes)))
                else:
                    className = getattr(entity_mod, classes[0])
                    new_entity = className(os.path.dirname(self.file),
                            e, self.controller)
            except AttributeError:
                print(entity_type + " not found")
                pass

            if not new_entity:
                print("creating a generic entity")
                new_entity = entity.Entity(os.path.dirname(self.file),
                        e, self.controller)
            # TODO: sort out the entities
            self.entities.append(new_entity)

    def get_entities(self):
        return self.entities
    
    def get_no_nondaemons(self):
        count = 0
        for e in self.get_entities():
            if e.daemon == False:
                count += 1
        self.nondaemons = count

    def run(self):
        for e in self.get_entities():
            e.run()
        self.get_no_nondaemons()

    def update(self):
        for e in self.get_entities():
            e.update()

    def end(self):
        while 1:
            self.update()
            if self.nondaemons == self.check_nondaemons():
                self.stop_daemons()
                break

    def stop_daemons(self):
        for e in self.get_entities():
            if e.daemon == True:
                e.stop()         
        
    def check_nondaemons(self):
        count = 0
        for e in self.get_entities():
            if e.container.status == "exited" and e.daemon == False:
                count += 1

        return count

# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

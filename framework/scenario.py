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
import time
from framework.entities import entity
from datetime import datetime
import subprocess

LOGS_DIR = "logs"
NETWORK_CAP = "net_capture"

class Scenario():

    def __init__(self, file, config, controller):
        self.p = None
        self.controller = controller
        self.config = config
        self.file = file
        self.dirname = os.path.dirname(file)
        self.entities = []
        self.get_scenario_timestamp()
        if "timeout" in config.keys():
            self.timeout = config["timeout"]
        else:
            self.timeout = 0

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

    def run(self):
        for e in self.get_entities():
            e.run()

    def update(self):
        for e in self.get_entities():
            e.update()

    def wait_end(self):
        wait = True
        counter = 0
        if self.timeout != 0:
            counter = self.timeout * 10; # 1000 ms / 100 (a cycle) -> 10 cycles per sec
        while wait or (self.timeout!=0 and counter==0):
            wait = False
            # see if we still have "running" "non-daemons"
            for e in reversed(self.get_entities()):
                if e.daemon == False and e.container.status != "exited":
                    wait = True
            if wait:
                time.sleep(0.1)  #sleep 100 ms before rechecking
                self.update()
                counter -= 1
        if wait:
            print(datetime.utcnow(), "- WARNING: not all entities self-terminated, end-forcing due timeout");
        # stop all remaining containers
        self.stop_all()

    def stop_tcpdump(self):
        if self.p:
            print(datetime.utcnow(), "- Tcpdump ended!")
            self.p.terminate()
        time.sleep(0.5)

    def stop_all(self):
        for e in self.get_entities():
            if e.container.status != "exited":
                e.stop()
                print(datetime.utcnow(), e.name, "- ExitCode: ", e.get_exit_code())
            else:
                print(datetime.utcnow(), e.name, "- ExitCode: ", e.get_exit_code())


    def create_dir(self, dir, searching_dir):
        if searching_dir not in os.listdir(dir):
            path = os.path.join(dir, searching_dir)
            os.mkdir(path)
            print(datetime.utcnow(), "- {} dir created successfully!".format(searching_dir))
        else:
            print(datetime.utcnow(), "- {} dir already exists!".format(searching_dir))

    def get_logs(self):
        self.create_dir(self.dirname, LOGS_DIR)
        logs_path = os.path.join(self.dirname, LOGS_DIR)
        for entity in self.entities:
            name = str(self.timestamp) + "_" + entity.container.name
            log_file = os.path.join(logs_path, name)
            f = open(log_file, 'w')
            f.write(entity.container.logs().decode('UTF-8'))
            f.close()
            print(datetime.utcnow(), "- Logs for {} fetched successfully!".format(entity.container.name))


    def start_tcpdump(self):
        res = "osbr0"
        self.create_dir(self.dirname, LOGS_DIR)
        dir = os.path.join(self.dirname, LOGS_DIR)
        capture_file = os.path.join(dir, str(self.timestamp) + "_cap.pcap")
        self.p = subprocess.Popen(['tcpdump', '-i', res, '-w', capture_file], stdout=subprocess.PIPE)
        # wait for proc to start
        time.sleep(0.5)

    def get_scenario_timestamp(self):
        self.timestamp = int(datetime.utcnow().timestamp())

    def get_status(self):
        self.create_dir(self.dirname, LOGS_DIR)
        logs_path = os.path.join(self.dirname, LOGS_DIR)
        for entity in self.entities:
            name = str(self.timestamp) + "_" + entity.container.name + "_STATUS"
            log_file = os.path.join(logs_path, name)
            f = open(log_file, 'w')
            f.write(entity.container.name + " " + str(entity.container.image) + " ExitCode: " + str(self.get_exit_code(entity.container)))
            f.close()
            print(datetime.utcnow(), "- Status for {} fetched successfully!".format(entity.container.name))

    def get_exit_code(self, container):
        return container.attrs["State"]["ExitCode"]

    def print_status(self):
        for entity in self.entities:
            print(datetime.utcnow(), "Name: {}, ExitCode: {}".format(entity.container.name, self.get_exit_code(entity.container)))

    def verify_test(self):
        ok = True
        for entity in self.entities:
            if self.get_exit_code(entity.container) != 0:
                ok = False
                break
        if ok == False:
            print(80*"=")
            print(datetime.utcnow(), "Test: {}".format(os.path.basename(self.dirname)))
            self.print_status()
            print(datetime.utcnow(), "TEST FAILED!")
            print(80*"=")
        else:
            print(80*"=")
            print(datetime.utcnow(), "Test: {}".format(os.path.basename(self.dirname)))
            self.print_status()
            print(datetime.utcnow(), "TEST PASSED!")
            print(80*"=")

    def __del__(self):
        pass
            
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

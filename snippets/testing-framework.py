import os
import yaml
import docker
import sys
import argparse

parser = argparse.ArgumentParser(description='Testing Framework for OpenSips Solutions')
parser.add_argument('tests', type=str, help='Tests director')
args = parser.parse_args()

class Controller:
    def __init__(self):
        pass

    def init_docker(self):
        return docker.from_env()

    def parser(self, file):
        with open(file, 'r') as stream:
            try:
                cfg_stream = yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                print(exc)

        return cfg_stream

    def entity_params(self, stream, entities, dir_path):
        for e in stream["entities"]:
            path = dir_path
            type = e["type"]
            image = e["image"]
            ip = e["ip"]
            ports = e["port"]
            #print(ports)
            dict = {}
            for p in ports:
                dict[p] = None

            if "mount" in e.keys():
                mount = e["mount"]
            else:
                mount = ""

            if "parameters" in e.keys():
                parameters = e["parameters"]
            else:
                parameters = ""

            if "config_file" in e.keys():
                config_file = e["config_file"]
            else:
                config_file = "default"

            if "scenario_file" in e.keys():
                scenario_file = e["scenario_file"]
            else:
                scenario_file = "default"
                
            if "name" in e.keys():
                name = e["name"]
            else:
                name = "-"

            entity = Entity(type, name, image, parameters, ip, dict, config_file, scenario_file, path, mount)
            entities.append(entity)

    def create_entities(self, tests_path, entities):
        for dir in os.listdir(tests_path):
            dir_path = tests_path + dir + "/"
            if scenario in os.listdir(dir_path):
                cfg_stream = controller.parser(dir_path + scenario)
                controller.entity_params(cfg_stream, entities, dir_path)
        
class Entity:
    def __init__(self, type, name, image, parameters, ip, ports, config_file, scenario_file, path, mount):
        self.name = name                    # mandatory
        self.type = type                    # mandatory
        self.image = image                  # mandatory
        self.parameters = parameters        # container run parameters optional
        self.ip = ip                        # mandatory
        self.ports = ports                  # mandatory
        self.config_file = config_file      # cfg file optional
        self.scenario_file = scenario_file  # scenario file optional
        self.path = path                    # autocompleted
        self.mount = mount

    def run_container(self, client):
        print(self.parameters)
        print(self.path)
        if self.type == "opensips":
            container = client.containers.run(self.image, self.parameters, detach=True)
            print(self.image + " " + container.status)
        elif self.type == "uas-sipp":
            container = client.containers.run(self.image, self.parameters, detach=True)
            print(self.image + " " + container.status)
        else:
            pass
        
        while(1):
            # updateing status
            container.reload()
            if container.status == "created":
                print("container just created, wait for changeing status")
                continue
            elif container.status == "exited":
                print("container terminated")
                break
            # container still running
            else:
                print("the container will stop")
                container.stop()
                container.reload()

controller = Controller()

client = controller.init_docker()

scenario = "scenario.yml"
tests_path = os.getcwd()+"/" + args.tests

entities = []
controller.create_entities(tests_path, entities)

for e in entities:
    if e.type == "uas-sipp":
        e.parameters = "-sn uas"
        e.run_container(client)
    elif e.type == "opensips":
        if e.config_file == "default":
            e.parameters = ""
        else:
            e.parameters = "-f /etc/opensips/opensips.cfg"
        e.run_container(client)
            

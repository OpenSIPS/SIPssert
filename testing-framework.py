import os
import yaml
import docker

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
        
class Entity:
    def __init__(self, type, name, image, parameters, ip, port, config_file, scenario_file):
        self.name = name                    # mandatory
        self.type = type                    # mandatory
        self.image = image                  # mandatory
        self.parameters = parameters        # container run parameters optional
        self.ip = ip                        # mandatory
        self.port = port                    # mandatory
        self.config_file = config_file      # cfg file optional
        self.scenario_file = scenario_file  # scenario file optional

    def run_container(self, client):
        container = client.containers.run(self.image, self.parameters, detach=True)
        print(self.image + " " + container.status)
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
tests_path = os.getcwd()+"/tests/"
entities = []

for dir in os.listdir(tests_path):
    dir_path = tests_path + dir + "/"
    if scenario in os.listdir(dir_path):
        cfg_stream = controller.parser(dir_path + scenario)
        for e in cfg_stream["entities"]:
            type = e["type"]
            image = e["image"]
            ip = e["ip"]
            port = e["port"]

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

            entity = Entity(type, name, image, parameters, ip, port, config_file, scenario_file)
            entities.append(entity)

for e in entities:
    if e.type == "uas-sipp":
        e.parameters = "-sn uas"
        e.run_container(client)
            

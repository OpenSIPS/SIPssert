import os
import yaml
import docker

class controller:
    def __init__(self):
        client = docker.from_env()
        return client
        
class container:
    def __init__(self, image, parameters, ip, port):
        self.image = image
        self.parameters = parameters
        self.ip = ip
        self.port = port

    def run_container(self, client):
        container = client.containers.run(self.image, self.parameters, self.ip, self.port)

def parser(file):
    with open(file, 'r') as stream:
        try:
            cfg_stream = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)

    return cfg_stream

def run_container(img, params, detached):
    # return a client configured from environment variables.
    client = docker.from_env()
    # run a container
    container = client.containers.run(img, params, detach=detached)
    print(img + " " + container.status)
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



uas = "uas-sipp"
uac = "uac-sipp"

opensips = "opensips"

uas_img = "ctaloi/sipp"
uas_params = "-sn uas"

uac_img = "ctaloi/sipp"
uac_params = "-sn uac"

#home path
home_dir = os.getcwd()
#tests path
tests_dir = home_dir+"/tests/"
#change dir to "tests"
os.chdir(tests_dir)

directoryes = os.listdir()

for dir in directoryes:
    os.chdir(tests_dir+dir)
    yaml_file = os.listdir()[0]
    cfg = parser(yaml_file)
    for e in cfg["entities"]:
        if e["type"] == uas:
            print("====================")
            run_container(uas_img, uas_params, True)
        elif e["type"] == uac:
            print("=========================")
            



from docker.api import volume
import entity
import docker
import argparse
import parser
import os

class Controller:
    def __init__(self):
        arg_parser= argparse.ArgumentParser(description='Testing Framework for OpenSips Solutions')
        arg_parser.add_argument('tests', help='Absolute path of the tests director', type=os.path.abspath)
        self.args = arg_parser.parse_args()
        self.dir_parser = parser.Parser(self.args.tests)

        self.client = docker.from_env()
        try:
            self.client.networks.get("controllerNetwork").remove()
        except docker.errors.APIError as err:
            if type(err) == docker.errors.NotFound:
                print("Network not found!")
            else:
                print("Something eles went wrong!")
        finally:
            print("New network can be created!")

        try:
            ipam_pool = docker.types.IPAMPool(subnet='192.168.52.0/24', gateway='192.168.52.254')
            ipam_config = docker.types.IPAMConfig(pool_configs=[ipam_pool])
            self.client.networks.create("controllerNetwork", driver="bridge", ipam=ipam_config)
        except docker.errors.APIError as err:
            print(type(err))

        
if __name__ == '__main__':
    entities = []
    controller = Controller()
    print(controller.client.networks.get("controllerNetwork"))
    dirs = controller.dir_parser.iterateTestsDir()
    for dir in dirs:
        stream = controller.dir_parser.parseScenario(controller.args.tests+"/"+dir)
        controller.dir_parser.streamToEntities(stream, entities)

    for e in entities:
        if e.type == "uas-sipp":
            params = "-sn uas" + e.getExtraParams()
            container = controller.client.containers.run(e.image, params, detach=True)
        elif e.type == "opensips":
            mount_point = e.getMountPoint()
            path_config = os.path.abspath(e.getPathConfig())
            params = "-f " + "/etc/opensips/opensips.cfg" + e.getConfigFile()
            print(path_config)
            print(mount_point)
            print(params)
            container = controller.client.containers.create(e.image, detach=True)
            controller.client.networks.get("controllerNetwork").connect(container, ipv4_address=e.ip)
            
            container.start()



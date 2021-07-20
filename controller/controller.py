import container
import docker
import argparse
import parser
import os

class Controller:
    def __init__(self):
        self.client = docker.from_env()
        arg_parser= argparse.ArgumentParser(description='Testing Framework for OpenSips Solutions')
        arg_parser.add_argument('tests', help='Absolute path of the tests director', type=os.path.abspath)
        self.args = arg_parser.parse_args()
        self.dir_parser = parser.Parser(self.args.tests)

if __name__ == '__main__':
    controller = Controller()
    dirs = controller.dir_parser.iterateTestsDir()
    for dir in dirs:
        stream = controller.dir_parser.parseScenario(controller.args.tests+"/"+dir)

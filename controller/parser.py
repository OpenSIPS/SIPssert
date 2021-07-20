import os
import yaml

SCENARIO = "scenario.yml"

class Parser():
    def __init__(self, root_path):
        self.root_path = root_path

    def iterateTestsDir(self):
        list_dirs = []
        for dir in os.listdir(self.root_path):
            list_dirs.append(dir)

        return list_dirs

    def yamlParser(self, file):
        with open(file, 'r') as stream:
            try:
                cfg_stream = yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                print(exc)

        return cfg_stream

    def parseScenario(self, dir):
        print(dir)

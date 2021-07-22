import os
import yaml
import entity

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
        stream = ""
        if SCENARIO in os.listdir(dir):
            stream = self.yamlParser(dir+"/"+SCENARIO)
        else:
            print("File does not exist!")
        
        return stream

    def streamToEntities(self, stream, entities):
        for e in stream["entities"]:
            if e["type"] == "uas-sipp":
                if "extra_params" in e.keys():
                    extra_params = e["extra_params"]
                else:
                    extra_params = ""
                container = entity.Entity_uas(e["name"], e["type"], e["image"], e["ports"], e["ip"])
                container.setExtraParams(extra_params)
                entities.append(container)
            elif e["type"] == "uac-sipp":
                if "extra_params" in e.keys():
                    extra_params = e["extra_params"]
                else:
                    extra_params = ""
                container = entity.Entity_uac(e["name"], e["type"], e["image"], e["ports"], e["ip"])
                container.setExtraParams(extra_params)
                entities.append(container)
            elif e["type"] == "opensips":
                if "extra_params" in e.keys():
                    extra_params = e["extra_params"]
                else:
                    extra_params = ""
                container = entity.Entity_opensips(e["name"], e["type"], e["image"], e["ports"], e["ip"])
                container.setExtraParams(extra_params)
                container.setMountPoint(e["mount_point"])
                container.setPathConfig(e["path_config"])
                container.setConfigFile(e["config_file"])
                entities.append(container)
            else:
                pass


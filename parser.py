import os
import yaml

no_tests = 1
tests_dir = "tests"
home = os.getcwd()
os.chdir(tests_dir)
controller_path = home+"/"+"controller.py"
controller_run = "sudo python3 " + controller_path

for i in os.listdir():
    os.chdir(home+"/"+tests_dir+"/"+i)
    cfg_file = os.listdir()[0]
    with open(cfg_file, 'r') as stream:
        try:
            cfg_stream = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)

    for j in cfg_stream["entities"]:
        for n in j:
            print(n)
    #print(cfg_stream["entities"])
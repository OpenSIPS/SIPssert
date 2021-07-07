import os
import yaml

no_tests = 1
tests_dir = "tests"
home = os.getcwd()
os.chdir(tests_dir)

for i in os.listdir():
    os.chdir(home+"/"+tests_dir+"/"+i)
    cfg_file = os.listdir()[0]
    with open(cfg_file, 'r') as stream:
        try:
            cfg_stream = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)

    for j in cfg_stream["entities"]:
        if j == "uas":
            os.system("sudo python3 /home/liviu/Desktop/proiect/testing-framework/controller.py")
    

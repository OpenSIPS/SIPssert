import sys, json, yaml

print(json.dumps(yaml.safe_load(open(sys.argv[1]))))

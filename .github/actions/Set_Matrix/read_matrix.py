"""Filters the OS and tests from the matrix file"""
import sys
import json
import yaml

matrix_keys = [ "os", "tests" ]

matrix_dict = yaml.safe_load(open(sys.argv[1], encoding="utf-8"))

print(json.dumps(dict(filter(lambda p: p[0] in matrix_keys,
                             matrix_dict.items()))))

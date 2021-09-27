## Usage

Run using docker priviledged user:
```
export PYTHONATH=.
bin/testing-framework tests
```

If running using `sudo`, you need to preserve the `PYTHONPATH` variable:
```
sudo -E env PYTHONPATH=. bin/testing-framework tests_sets/set_one
```

Alternatively, configure sudo to bypass the `PYTHONPATH` variable: add in the
`/etc/sudoers.d/python` (or direcly in `/etc/sudoers`) the following line:
```
Defaults env_keep += "PYTHONPATH"
```

Available parameters:
```
Config: --config /framework/global_config.yml; Default value: default_config.yml
Test: --test tests_sets/set_one/first_test/; Default value: All (will run all the tests from the sets specified)
```

Mandatory parameters for running: at least one set of tests
```
sudo -E env PYTHONPATH=. bin/testing-framework tests_sets/set_one
```

If testing many sets: list of sets
```
sudo -E env PYTHONPATH=. bin/testing-framework tests_sets/set_one/ tests_sets/set_two/ tests_sets/set_three/ --config global_config.yml
```

If testing only one test from a set: tests_sets/set/ --test tests_sets/set/first_test/ 
```
sudo -E env PYTHONPATH=. bin/testing-framework tests_sets/set_one/ --test /tests_sets/set_one/first_test
```

## Usage

Run using docker priviledged user:
```
export PYTHONATH=.
bin/testing-framework tests
```

If running using `sudo`, you need to preserve the `PYTHONPATH` variable:
```
sudo -E env PYTHONPATH=. bin/testing-framework tests_sets/sample_tests
```

Alternatively, configure sudo to bypass the `PYTHONPATH` variable: add in the
`/etc/sudoers.d/python` (or direcly in `/etc/sudoers`) the following line:
```
Defaults env_keep += "PYTHONPATH"
```

Available parameters:
```
Config: --config /framework/global_config.yml; Default value: `config.yml`
Test: --test 01.calling; Default value: none (will run all the tests from the sets specified)
```

Mandatory parameters for running: at least one set of tests
```
sudo -E env PYTHONPATH=. bin/testing-framework tests_sets/local_tests/
```

If testing many sets: list of sets
```
sudo -E env PYTHONPATH=. bin/testing-framework tests_sets/local_tests/ tests_sets/opensips.org_tests/ tests_sets/sample_tests/ --config global_config.yml
```

If testing only one test from a set: tests_sets/set/ --test first_test
```
sudo -E env PYTHONPATH=. bin/testing-framework tests_sets/local_tests/ --test 03.register_cli
```

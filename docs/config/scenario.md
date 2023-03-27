# SIPssert Testing - Scenario Configuration File

Each scenario has a mandatory configuration file in the
[YAML](https://yaml.org/) format that resides in the `SCENARIO/scenario.yml`
file, and describes how the test/scenario should be executed.

## Settings

Each scenario can have one of the following settings:

* `network`: describes the network device used for this scenario; available
values are described in tests set [Networks](tests-set.md#neworks); this value
is optional, and if missing, the tests set `network` value is considered
* `networks`: similar with `network`, but defines additional networks to be
used; if missing, no extra network is being used
* `timeout`: a timeout, expressed in seconds, for running the entire scenario;
this value is optional, and if it is missing, the tasks do not timeout ever
* `init_tasks`: a list of tasks as described in [Tasks](../tasks.md) that
should be run before running the scenario's tasks (in the `tasks` node); this
value is optional, and if it is missing, no initial tasks are executed
* `tasks`: a list of tasks as described in [Tasks](../tasks.md) that represent
the tasks that should be run for a particular scenario; this parameter is
mandatory and at least a task should be specified
* `cleanup_tasks`: a list of tasks as described in [Tasks](../tasks.md) that
should be run after the `tasks` list is completed; similar to `init_tasks`,
this parameter is optional

## Example

A simple scenario that starts an OpenSIPS server on the host network can be
specified like this:
```
---
network: host
timeout: 10
tasks:
  - name: OpenSIPS
    type: opensips
```

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
* `volumes`: a list of volumes that should be created when running the scenario;
this parameter is optional, and if it is missing, no volumes are created; the
volumes are created using `local` driver; binding directory and permissions can
be specified using the `bind` and `mode` keys, respectively; if defined, these
values will be used as defaults when a task is using the volume, but they can be
overridden in the task definition; these values can also be omitted at the
scenario level, but in this case, the task should define them; volumes are created
at the beginning of the scenario, **used only by the tasks that have them specified**,
and removed at the end of the scenario;

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

This is an example on how to use `volumes` in a scenario, where volumes have
default values for `bind` and `mode`:
```
---
network: host
timeout: 10
tasks:
  - name: Task 1
    type: generic
    image: some_image
    volumes:
      - volume_1

  - name: Task 2
    type: generic
    image: some_image
    volumes:
      - volume_1
      - volume_2

  - name: Task 3
    type: generic
    image: some_image
    volumes:
      volume_1:
        bind: /tmp
        mode: rw
      volume_2:
        bind: /tmp
        mode: ro

  - name: Task 4
    type: generic
    image: some_image
    volumes:
      volume_1:
      volume_2:
        mode: rw

volumes:
  volume_1:
    bind: /var/tmp
    mode: rw
  volume_2:
    bind: /tmp
    mode: ro
```

This is an example on how to use `volumes` in a scenario, where volumes don't
have default values for `bind` and `mode`:
```
---
network: host
timeout: 10
tasks:
  - name: Task 1
    type: generic
    image: some_image
    volumes:
      volume_1:
        bind: /tmp
        mode: rw

  - name: Task 2
    type: generic
    image: some_image
    volumes:
      volume_2:
        bind: /var/tmp
        mode: ro

volumes:
  - volume_1
  - volume_2
```

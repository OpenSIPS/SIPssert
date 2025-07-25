# SIPssert Testing Framework Tasks

Tasks are probably the most important asset of the testing framework, as they
control the applications that are being executed in order to verify your setup.
On a high level perspective, the purpose of tasks is to simplify the control of
the underlying application by providing a control interface in the scenario. At
low level, a task is essentially translated to a docker container that is run
with specifically configured parameters/settings.

In the scenario, you specify a list of tasks. Each task defined should have a
`type` node (if missing, `generic` is assumed). This value identifies the task
type that should be run. For each task, multiple settings can be defined: part
of them are generic tasks settings (as described in the [Settings](#settings)
section), and part are tasks specifics. Each specific task's settings should be
documented in the [tasks](tasks) directory.

## Execution

The way tasks are executed by the framework is described in the
[Execution](execution.md) page.

## Settings

Each task, regardless of its type, can contain one of the settings. Most of
these settings are interpreted by the testing framework itself, but they can be
inherited by the tasks as well. The generic settings are found below. Note that
only the `name` node is mandatory, all the others are optional.

* `name`: mandatory, represents the name of the task, which should be unique
among the scenario.
* `type`: the task type, which indicates how the task should be executed. if
missing, the `generic` type is assumed. Available tasks type can be found in
the [tasks](tasks) directory.
* `image`: the Docker image that should be used to run this task; if missing,
the image declared in the specific task's implementation is used; if there is
no image defined in the task (such as for the `generic` case), the execution
will fail.
* `network`: a valid network's name, as defined in the tests set
[networks](config/tests-set.md#networks) settings; if missing, the scenario's
`network` configuration is used
* `networks`: a list of network configurations that need to be assigned to the
task, in addition to the default `network`; if the element is a string, it
represents the name of the network to be assigned, otherwise, it can be an
object consisting of the following nodes:
 * `network`: mandatory, the network adaptor's name , as defined in the 
[networks](config/tests-set.md#networks) settings;
 * `ip`: optional, an IP within the network's range to be assigned;
 * `disabled`: a boolean that indicates that although the network has been
enabled, it should not be used (useful when defining a network at the tests
set level, but it is not needed for this task); defaults to `false`.
* `require`: defines the dependencies the task requires to execute, as
described in the [dependencies](dependencies.md) page; if missing, no
dependencies are used.
* `ready`: defines the dependencies that the task needs to satisfy in order to
become `ready`; the format is the same on as for the
[dependencies](dependencies.md); if missing, the task is ready immediately
after started.
* `delay_start`: a shortcut of the [Wait](dependencies.md#wait) dependency,
delays the start of this task with the number of seconds after the previous
task has been executed; deprecated, please use the [Wait](dependencies.md#wait)
dependency instead.
* `mount_point`: a path representing the mount point of the scenario directory;
defaults in the `/home` directory of the container, but may be overwritten by
the task implementation.
* `daemon`: boolean value, indicating whether the task should be considered a
`daemon` or a `non-daemon`; the default value is false, but it is usually
overwritten by the specific task implementation.
* `label`: a string that can be assigned to the task, that can be used later on
to reference it in the dependencies of a different task; if missing, no label
is defined and the task can only be identified by its name
* `labels`: a list of labels, with the same meaning of the single `label`
* `ip`: the IP address that should be assigned to the container when running in
the `bridge` network mode; if missing, a random IP within the range is
assigned; this value is being considered only for the `network` adaptor, the
adaptors in the `networks` node should have their own `ip` settings
* `port`: the port address that should be opened for the container when
running in `bridge` network mode; if missing, no port forwarding is created;
the format is `port[/protocol]`, where `protocol` can be either `udp`, `tcp` or
`sctp`, or missing; the port is being opened for any available network adaptor,
either in `network`, or in the `networks` one, if not explicitely overwritten.
* `ports`: a list of `port` nodes, used to exposed multiple ports
* `stop_timeout`: timeout to wait for a container to stop; if missing, or not
overwritten, it defaults to `0`/immediate stop
* `args`: a string containing either a string or a list of extra arguments that
should be sent when starting the container; these parameters are appended after
the arguments generated by the task implementation; if missing, no extra
parameters are used.
* `env_file`: path to a file containing environment variables that should be
set when running the container.
* `env`: a dictionary containing environment variables that should be set
when running the container; variables defined here will overwrite
the ones defined in the `env_file`.
* `entrypoint`: can be used to overwrite the default entrypoint of the image.
* `healthcheck`: optional, a dictionary containing the healthcheck settings for
the container; if missing, image's default healthcheck is used; the dictionary
may contain the following nodes (as explained [here](https://docker-py.readthedocs.io/en/stable/containers.html)):
  * `test`: the command to run to check the health of the container
  * `interval`: the time between two consecutive health checks
  * `timeout`: the time to wait for the health check to complete
  * `retries`: the number of retries before considering the container unhealthy
  * `start_period`: the time to wait before starting the health checks
* `logging`: contains information about task logging
  * `console`: boolean indicating whether the logging should be dumped at
  console or not (Default: `false`)
* `checklogs`: RegEx patterns that should be checked for in the logs;
when a check fails, the task is considered failed; this node can either be a
list of strings, meaning that all of them should be found, or a dictionary with
the following nodes:
  * `all`: a list of strings that should be found in the logs
  * `none`: a list of strings that should not be found in the logs
* `volumes`: either a list of volumes that should be mounted in the container, or a
dictionary of volumes, each with the following nodes:
  * `bind`: the path to the directory where the volume should be mounted
  * `mode`: the permissions of the mounted volume; can be either `rw` or `ro`
omitting these keys works only if the volume is defined in the scenario
(see [Scenario](config/scenario.md#volumes) for more details);  if the
volume is defined outside of the scenario, it should be declared as a dictionary
with the `bind` and `mode` keys, otherwise an exception is raised.

You can find the specific settings for each task type in their corresponding
file in the  [tasks](tasks) directory.

## Examples

Running OpenSIPS server with a specific IP and port from the `osbr0` device and
a custom configuration file in `/tmp/opensips.cfg`, and an extra memory modifier.

``` 
network: osbr0
tasks:
  - name: OpenSIPS
    type: opensips
    ip: 192.168.52.52
    port: 5060
    config_file: /tmp/opensips.cfg
    args: -M32
```

Logging configuration should look like this:

```
tasks:
  - name: MySQL Server
    type: mysql
    ip: 192.168.52.64
    logging:
      console: true
```

Running a MySQL server with a custom healthcheck test (note that 
time parameters are expressed in **nanoseconds** and are **integers**, 
**either 0 or at least 1000000** (1ms)):

```
tasks:
  - name: MySQL
    type: mysql
    ...
    healthcheck:
      test: mysql opensips -e 'SHOW TABLES LIKE "version"' 2>&1 | grep -q version
      interval: 1000000000
      timeout: 1000000000
      start_period: 0
```

Running a task and check for patterns in the logs:

```
# patterns 1, 2 and 3 should be found, while patterns 4 and 5 should not be found

tasks:
  - name: MySQL
    type: mysql
    ...
    checklogs:
      all: regex1 regex2 regex3
      none:
        - regex4
        - regex5

# or

tasks:
  - name: MySQL
    type: mysql
    ...
    checklogs:
      all: regex1 regex2 regex3
      none: regex4 regex5

# if all patterns should be found

tasks:
  - name: MySQL
    type: mysql
    ...
    checklogs: regex1 regex2 regex3 regex4 regex5

# or

tasks:
  - name: MySQL
    type: mysql
    ...
    checklogs:
      all: regex1 regex2 regex3 regex4 regex5
```

Mounting an external volume in the container:

```
tasks:
  - name: MySQL
    type: mysql
    ...
    volumes:
      db_data:  # this is a volume defined outside the context of the scenario
        bind: /var/lib/mysql
        mode: rw
```

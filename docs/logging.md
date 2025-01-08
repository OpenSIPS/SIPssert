# SIPssert Testing Framework Logging

This page contains information about the events that are being logged by the
testing framework and the way they can be tuned. There are different types of
logging that are being performed at different levels.

Every execution of the `sipssert` tool creates a unique directory of the run
in the logs directory defined by the `-l` parameter (see
[Usage](../README.md#usage) for more details. The name of this directory is
constructed according to the `%Y-%m-%d.%H:%M:%S.%f` format (i.e.
`2023-02-16.09:45:21.385016`) and represents the time (down to microseconds)
when the `sipssert` tool was executed. For convenience, a symbolic link named
`latest` is created in the logs directory, and is pointed to the latest run
every time. We will refer to this directory as `RUNDIR` throughout the page.

Each of the following components dump their logs in this directory, or one of
its subdirectories. See [this example](#example) for a common idea of how the
logs hierarchy can look like.

## Testing

The testing component is the one that displays the status of the scenarios that
have been run. This status is always printed at standard out, and on each line
you can find the scenario that is being run along with its status (PASS, FAIL,
TOUT, etc.).

At the end of the execution you are presented a summary of the execution, with
a total count of scenarios, how many of them were successful and how many were
failed.

## Controller

The controller is the main component of the framework and is in charge of
managing, scheduling and executing all the testing entities, from the tests set
level, down to the tasks level. Each of its decision, action, or error is being
logged at a different logging level.

By default, the controller logging is dumped in the `RUNDIR/controller.log`
file, and by default only *INFO* messages and higher are displayed. This,
however, can be modified through the [Running
Configuration](docs/config/run.md) file, which can also instruct to write
the logs at standard output. This option is however not recommended, as it
hinders the visibility of the testing status. 

Among the events that are being logged by the controller are:
 * the parameters a task is being started with
 * the moment a task is being started/stopped/terminated
 * tasks exit status
 * dependencies between tasks

## Tests Set

For each tests set being run, a directory is created under the `RUNDIR`
directory, named exactly as the tests set directory is named. For example, when
running the tests sets in the `/home/tests/registration` directory, the
`RUNDIR/registration` directory will be created. We will refer to the directory
of each tests set as `SETDIR` from this point forward.

If the tests set has a list of `init_tasks` defined, each task within the list
will dump its logs in the `SETDIR/init_tasks` directory. Similarly for the
`cleanup_tasks` defined for a tests set.

## Scenario

Each scenario creates its own directory in the `SETDIR` directory, named just
as the scenario is named. Each task run for this scenario (including
`init_tasks` and `cleanup_tasks`, if defined) will dump their logs in this
directory. We will refer to this directory as `SCENDIR`.

## Task

Each task generates two files in the `SCENDIR` directory:
* *`task_name`*`.status` - contains the exit code of the task/container
* *`task_name`*`.log` - contains the logs of the application (fetched by the
`docker logs` command)

## JUnit report

You are allowed to generate junit compatible test report in xml that can
be read by any available junit test reporter action in GitHub. So you can set up
your workflow by generating junit report from sipssert run and passing report
into reporter action on your own to display test result in convinient way
on GitHub run summary.

Add `junit: yes` into `run.yml` config file or pass `--junit-xml` command-line
parameter into sipssert command when running test to generate junit report.
Generated report will be saved into `logs/latest` directory as `report.xml`.

## Example

A common hierarchy of a run would look something like this:
```
/logs
├── 2023-02-16.15:36:56.662055
│   ├── controller.log
│   ├── tests-set-1
│   │   ├── 01.scenario1
│   │   │   ├── cleanup.log
│   │   │   ├── cleanup.status
│   │   │   ├── init.log
│   │   │   ├── init.status
│   │   │   ├── task1.log
│   │   │   ├── task1.status
│   │   │   ├── task2.log
│   │   │   └── task2.status
│   │   ├── 02.scenario1
│   │   │   ├── task1.log
│   │   │   └── task1.status
│   │   ├── cleanup_tasks
│   │   │   ├── clean.log
│   │   │   └── clean.status
│   │   └── init_tasks
│   │       ├── init.log
│   │       └── init.status
│   └── tests-set-2
│       └── ...
└── latest -> 2023-02-16.15:36:56.662055
```

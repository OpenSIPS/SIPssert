# SIPssert Testing Framework Tasks Execution

At application startup, before executing the task, the engine gathers
information about how it should be run (i.e. what IP should it listen on, what
port(s), mounted directories, etc). These are generically interpreted by the
engine and used to instruct the Docker engine behaviour. The particular/per
task settings are passed along to the implementation of each task, and are used
to modify the way the underlying container is run, through container arguments,
environment, mount points, etc.  Implementation of each task resides in the
[tasks source](../sipssert/tasks) directory).

Once all tasks descriptions among all scenarios are compiled, execution of the
scenarios is started (read more about this in
[Execution](../README.md#execution)). When a particular task is to be executed,
it is first checked whether all its dependencies (see
[Dependencies](#dependencies) for more information), if existing, are
met - if they are not, its execution is postponed until these are satisfied.
Once they are, the following actions are performed by the engine:
 1. fetch container arguments and environment (from the task implementation)
 2. fetch networking mode it should run
 3. fetch the mounted volumes
 4. create the container
 5. attach the container to the networking device, providing required IPs and ports
 6. execute the task

## Mount points

Every task that is executed has mounted the host's scenario directory in the
container's home directory (the target depends on the container type) as a
read-only directory.

## Daemons

Executed tasks are organized in two categories: daemon and non-daemon. The
difference between them is that for the non-daemon tasks the engine expects to
finalize by their own, while for the daemon ones, the engine expects to never
finalize by their own, hence, they should be explicitly terminated at the end
of the scenario execution. If a daemon task finalizes by its own, it is
considered an error and the scenario fails.

## Dependencies

By default, all tasks within a tasks list (i.e. `init_tasks` or `tasks` node)
are executed in parallel. However, in practice, some tasks may require that
others have been started, or completed, before executed, thus a more complex
schedule is required. Dependencies are a way of providing information about
what tasks depend on others, in order to execute them in the correct order, at
the correct moment in time. Dependencies format is described
[here](dependencies.md).

## Scheduling

Scheduling is an iterative task, and when initially triggered, it executes all
the tasks that do not have any dependencies. Next, it is triggered either by
the termination of another task, or by a timeout. On every iteration, it goes
through the entire list of pending (not executed) tasks and checks if their
dependencies have been satisfied in the meantime, and if they have, the tasks
are executed. This process continues until there are no more tasks in the
pending list.

## Termination

Termination of execution is triggered either when all non-daemon tasks have
completed, either when the configured scenario timeout has been reached. Once
this happens, all running tasks are being stopped and terminated. A normal
termination means that only daemon tasks should have been remaining, therefore
terminating them would not result in errors. However, if a timeout triggers the
termination, if there is any pending task (executed or not even scheduled yet),
the scenario exits with a timeout value, and all the running tasks are
terminated (including daemon and non-daemon ones).

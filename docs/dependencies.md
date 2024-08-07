# SIPssert Testing Framework Tasks Dependencies

Dependencies are used to control the order of the tasks execution. This file
contains the list of available dependencies.  A task can have multiple
dependencies, that can be specified in three different forms: as strings, list
or dictionary:

* String format: When providing a string to the `require`/`ready` parameters,
the default [`After`](#after) dependency is assumed, and the value represents
the name of the task (or label) that the current tasks depends on.

* Dictionary format: When having multiple dependencies for a single task, if
the dependencies (types) are different, they can be specified as a dictionary:
```
 - name: Task2
   require:
     After: Task1
     Ready: Server
```

* List format: It is useful when having multiple dependencies with overlapping
types, such as:
```
 - name: Task2
   require:
     - After: Task1
     - After: Server
```

## After

This dependency is used to specify that a particular task should be executed
after a daemon task has been started, or a non-daemon task has been completed.

The content of the dependency is either a string, representing the name (or
label) of the task that needs to be waited, or a dictionary containing the
`task` node, which represents the same thing.

When the dictionary mode is used, an optional `wait` node can be specified as a
float value, and represents the number of seconds that should be waited after
the task dependency has been met, but before executing the task.

When using the dependencies parameters in the task without an explicit type, 
`After` is considered the default.

### Example

Execute `Task2` after `Task1` using the simple require form
```
 - name: Task2
   require: Task1
```

Same as above, but using the explicit dependency name
```
 - name: Task2
   require:
     After: Task1
```

Same as above, but using the long, dictionary, format
```
 - name: Task2
   require:
     After:
       task: Task1
```

If you want `Task2` to be executed 2s later after `Task1`, you should be using
the `wait` parameter, as below:
```
 - name: Task2
   require:
     After:
       task: Task1
       wait: 2
```

## Started

This is similar to the [After](#after) dependency, except that it considers
only the moment the dependent task has been started. This means that for a
daemon dependent task, it behaves just as the [After](#after) dependency, but
for a non-daemon one, it is satisfied once the task has been started, without
considering its termination.

It has the same syntax and meaning as the [After](#after) dependency.

## Delay

Delays the execution of a task after the previous task in the list has been
executed.

It receives a float as parameter representing the number of seconds to wait
after the previous task has been started.

### Example

Start `Task2` one second after `Task1` has been started, and `Task3` one second
after `Task2`:
```
tasks:
 - name: Task1
 - name: Task2
   require:
     delay: 1
 - name: Task3
   require:
     delay: 2
```
This would result in running `Task1`, after 1s `Task2`, and after another 1s,
`Task3`.

## Wait

Usually used in the `ready` dependencies, it represents the number of seconds
to wait after the task has been created.

Receives a float as parameter representing the number of seconds to wait.

### Example

Wait for MySQL to initialize for 1s before marking the task as ready:
```
 - name: MySQL
   type: mysql
   ready:
     wait: 1
```

## Ready

Similar to the [Started](#started) dependency, except that after the node has
been started, its `ready` dependencies are checked as well. This is useful when
a task depends on a daemon task that requires some time to initiate.

### Example

Start a mysql server that is ready after 1s, then start OpenSIPS that hooks
into it:
```
tasks:
 - name: MySQL
   type: mysql
   ready:
     wait: 1
 - name: OpenSIPS
   type: opensips
   require:
     Ready: MySQL
```

## Healthy

This dependency can be used to specify that a certain task should be executed after
the health-check of a task passed successfully (status is `healthy`). 

Content of the dependency is a string representing the name (or label) of the task 
that needs to be healthy.

### Example

Start OpenSIPS after MySQL database is initialized:
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
  
  - name: OpenSIPS
    type: opensips
    require:
      Healthy: MySQL
```

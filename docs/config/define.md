# SIPssert Testing Framework Definition files

Every scenario, and optionally every tests set, is described through a
configuration format file. These files usually contain a lot of information
that has to be passed down to the tasks run, and almost all the time the same
setting has to be shared among multiple tasks. The purpose of the definition
file, named `defines.yml` is to allow the scenario writers to provide a set of
definitions/variables, that can be later on shared in the configuration
configuration file of the scenario (and/or tests set) multiple times.

## Format

The `defines.yml` file is defined in the [YAML](https://yaml.org/), and each
setting has to be defined on a new line, on the root level.
For example, this is a valid defines file:

```
proxy_ip: 10.0.0.1
proxy_port: 5060
```

Note that the variables have to be final values (unless `getenv` filter is used), i.e. they cannot be expansions
of other values.

## Environment variables

Environment variables can be used in `defines.yml` file, by using the `getenv` filter.
For example, to use the value of some `MYSQL_IP` environment variable, you can define the following:

```
mysql_ip: {{ 'MYSQL_IP' | getenv }}
```

Default values can be provided as well, in case the environment variable is not set:

```
mysql_ip: {{ 'MYSQL_IP' | getenv('127.0.0.1') }}
```

## Use case

A simple use case would be testing registration for a SIP proxy, that is
listening on a specific IP:PORT. To test this, you need (at least) two tasks:
one that starts the SIP proxy, and another task that performs the registration.
Both of them need to share the same information, i.e. the IP:PORT to listen for
the proxy, and to register for the UAC. Of course, you may create the two
tasks, and specify the IP:PORT setting for each of them, duplicating the same
information. However, in time, due to several reasons, that IP:PORT might
change, and in order to adapt the change, you will need to go through each task
and modify the IP:PORT, and probably through each scenario, if you are (very
likely) testing several features.

This is where defines come handy: instead of writing the IP:PORT setting for
each task, you may define a custom variable in the tests set `defines.yml`
file, let's call it `proxy_ip_port`. Then, in each scenario, for each task,
instead of defining `setting: IP:PORT`, you may use `setting: {{ proxy_ip_port
}}`. That way, you are sure that sharing the information is not prone to error
(due to unexpected typos), and that if you ever want to change that setting,
you only need to change one value, that's it.

## Inheritance

Defines that are specified for tests sets are automatically inherrited by the
scenarios, unless explicitely overwritten at the scenario level.

# SIPssert Testing - Tests Set Configuration File

This document decribes the parameters that may be present for configuring a
tests set. It has a [YAML](https://yaml.org/) format and should be defined in
`TESTS_SET/config.yml` file. It is optional, and if it missing, default values
are considered.

## Settings

A tests set can have one of the following settings:

* `bridge_networks`: a list of bridge network descriptors that the scenarios
within this tests set might use; check below more information about
[Networks](#networks).
* `network`: describes the network device used for this scenario; available
values are described in [Networks](#networks); this value is optional, and if
missing, `host` is considered the default.
* `networks`: additional networks that are automatically assigned to all tasks
within this tests set. If missing, no aditional networks are being assigned.
* `defaults`: consists of a dictionary that specify a set of default settings
for the tasks that are being initiated within this tests set; more about this in
[Defaults](#defaults) section.
* `init_tasks`: a list of tasks as described in [Tasks](../tasks.md) that
should be run before running any scenario within this tests set; this value is
optional, and if it is missing, no initial tasks are executed
* `cleanup_tasks`: a list of tasks as described in [Tasks](../tasks.md) that
should be run after all the scenarios within the tests set are executed;
optional, and if missing no cleanup task is run

## Networks

Currently supporting networking modes are `host` and `bridge`. The `host` mode
does not require any explicit configuration, therefore it must not be specified
within the `networks` node of the tests set. However, a `bridge` needs to be
explictely specified in order to be created and configured properly.

### Bridge Settings

Each bridged network should consist of the following settings:
* `name`: the name of the bridge, mandatory
* `subnet`: the subnet that should be used, mandatory (example: `192.168.52.0/24`)
* `gateway`: the gateway that should be used, mandatory (example: `192.168.52.1`)
* `device`: the name of the device, optional, and if missing the `name` of the
bridge is assumed

### Bridge Example

An example of a bridge that uses the `192.168.52.0/24` network is:
```
  - name: osbr
    subnet: 192.168.52.0/24
    gateway: 192.168.52.1
    device: osbr0
```

## Defaults

The purpose of defaults is to minimize the length of scenarios by unifying
common settings under the `defaults` node of the test set. Defaults can be used
to specify default settings for a specific task type.  For example, for all the
scenarios within a specific tests set, you may always want to start the
OpenSIPS tasks with the same IP and port. This is where defaults become handy.

They are organized as a dictionary, where each key is the name of the task
type, that points to a new dictionary containing the default settings for that
specific task type. So the format is similar to:
```
defaults:
  type1:
    key1: value1
    key2: value2
  type2:
    key1: value1
    key2: value2
```

Check out [Example](#example) of defining default IP and port for all OpenSIPS
tasks.

## Example

An example of a tests set that defines the osbr0 network and uses it by
default, as well as setting OpenSIPS IP within that network can be described
below:
```
bridge_networks:
  - name: osbr0
    subnet: 192.168.52.0/24
    gateway: 192.168.52.1
network: osbr0

defaults:
  opensips:
    ip: 192.168.52.52
    port: 5060
```
All the subsequent instances of `opensips` within this tests set will have
OpenSIPS listening on ip `192.168.52.52` port 5060.

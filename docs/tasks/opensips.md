# SIPssert Testing Framework OpenSIPS CLI Task

Task used to execute [OpenSIPS](https://opensips.org/) server.

## Behavior

The task runs the `opensips` proxy server in a `daemon` container. One may
provide a custom configuration file, which is by default mounted in the
`/etc/opensips` directory.

## Defaults

The variables overwritten by default by the task are:

* `image`: default image to run is `opensips/opensips`
* `mount_point`: the scenario is initially mounted in the `/etc/opensips`
directory

## Settings

Additional settings that can be passed to the task:

* `socket`: optional, an OpenSIPS socket specified in the `proto:IP:port`
format; if missing, no socket is used, so the configuration file should
define its own
* `sockets`: similar to the `socket` node, but allows a list of sockets
* `config_file`: optional path to the OpenSIPS configuration file; if missing
the default `opensips.cfg` is being used

## Example

Run a trunking setup, where the `trunking.cfg` file is located in the
scenario's directory.

```
 - name: OpenSIPS Server
   type: opensips
   config_file: /etc/opensips/trunking.cfg
```

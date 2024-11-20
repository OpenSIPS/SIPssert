# SIPssert Testing Framework OpenSIPS MI Task

Task used to run a MI command using the [OpenSIPSMI Python module](https://github.com/OpenSIPS/python-opensips). It is designed to be more lightweight than its alternative, the [OpenSIPS CLI](./opensips-cli.md) task, stripping down the unnecessary features and focusing on the MI commands.

## Behavior

The task is able to communicate with one or more OpenSIPS instances using the
[OpenSIPSMI Python module](https://github.com/OpenSIPS/python-opensips/blob/main/docs/mi.md) over HTTP, Datagrams or FIFO files. It has two different working modes: running a single command, or
running a script, either with the `.sh` (executed with bash), either a `.py`
file (executed with Python).

## Defaults

The variables overwritten by default by the task are:

* `image`: default image to run is `opensips/python-opensips`

## Settings

Additional settings that can be passed to the task:

* `script`: optional, a path to a `.sh` or `.py` script that can be executed;
if missing, the `opensips-mi` tool will execute the command that is passed through the `args` parameter (see the example below)
* `mi_ip`: optional, the IP to the OpenSIPS MI listener; if missing,
`127.0.0.1` is used
* `mi_port`: optional, the port to the OpenSIPS MI listener; if missing,
`8888` is used
* `mi_type`: optional, the type of the MI connection; if missing, `http` is used

## Examples

```
 - name: Reset Statistics
   type: opensips-mi
   args: reset_all_statistics
```

```
 - name: Check Domain
   type: opensips-mi
   script: check_domain.py
   args: domain.sip

   # check_domain.py is a Python script that uses the OpenSIPSMI module to execute the MI command `domain_dump` and search for `domain.sip`
```
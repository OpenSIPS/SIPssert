# SIPssert Testing Framework OpenSIPS CLI Task

Task used to run a command using the [OpenSIPS
CLI](https://github.com/OpenSIPS/opensips-cli) tool.

## Behavior

The task is able to communicate with one or more OpenSIPS instances using the
[OpenSIPS CLI](https://github.com/OpenSIPS/opensips-cli) tool over the MI HTTP
interface. It has two different working modes: running a batch command, or
running a script, either with the `.sh` (executed with bash), either a `.py`
file (executed with python). You may also provide a custom configuration file
that can be automatically loaded.

## Defaults

The variables overwritten by default by the task are:

* `image`: default image to run is `opensips/opensips-cli`

## Settings

Additional settings that can be passed to the task:

* `script`: optional, a path to a `.sh` or `.py` script that can be executed;
if missing, the `opensips-cli` tool is executed
* `mi_ip`: optional, the IP to the OpenSIPS http MI listener; if missing,
`127.0.0.1` is used
* `mi_port`: optional, the port to the OpenSIPS http MI listener; if missing,
`8888` is used
* `mi_path`: optional, the path to the OpenSIPS http MI listener; if missing,
`mi` is used
* `config_file`: optional configuration file with default settings that is
passed to `opensips-cli` as the `-f` parmeter

## Example

Create a user using the OpenSIPS CLI tool.

```
 - name: Create a User
   type: opensips-cli
   args: -x add user testing@opensips.org
```

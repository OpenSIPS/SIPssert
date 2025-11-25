# SIPssert Testing - Run Configuration File

This configuration file is used to tune global runtime parameters, such as
logging, tests, etc. It should be defined as a [YAML](https://yaml.org/) and its path
defaults to `run.yml`.
If a `defines.yml` file exists in the same directory, it is loaded and its
definitions are expanded according to the Jinja2 format.

## Settings

The run configuration file consists of the following settings:

* `logging`: contains information about logging
  * `controller`: provides information about controller logging
    * `file`: the file where controller logging is dumped (Default: `controller.log`)
    * `console`: boolean indicating whether the logging should be dumped at console or not (Default: `false`)
    * `level`: debugging level of the controller (Default: `INFO`)
    * `timestamp`: adds timestamp to genereated logs (Default: `true`)
* `tests`: a list of tests sets to run - these represent the default set of
tests to be run, unless specified as arguments otherwise (Default: current
working directory)
* `test`: a list of test filters to be used unless specified as arguments
through the (`-t|--test` argument) (Default: empty)
* `exclude`: a list of exclude filters to be used unless specified as
arguments through the (`-e|--exclude` argument) (Default: empty)

## Example

The default running configuration file should look like this:
```
---
logging:
  controller:
    console: false
    level: INFO
    file: controller.log
tests:
  - .
```

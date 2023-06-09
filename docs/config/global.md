# SIPssert Testing - Global Configuration File

This configuration file is used to tune global runtime parameters, such as
logging. It should be defined as a [YAML](https://yaml.org/) and its path
defaults to `global.yml`.
If a `defines.yml` file exists in the same directory, it is loaded and its
definitions are expanded according to the Jinja2 format.

## Settings

The global configuration file consists of the following settings:

* `logging`: contains information about logging
  * `controller`: provides information about controller logging
    * `file`: the file where controller logging is dumped (Default: `controller.log`)
    * `console`: boolean indicating whether the logging should be dumped at console or not (Default: `false`)
    * `level`: debugging level of the controller (Default: `INFO`)
    * `timestamp`: adds timestamp to genereated logs (Default: `true`)

## Example

The default global configuration file should look like this:
```
---
logging:
  controller:
    console: false 
    level: INFO
    file: controller.log
```

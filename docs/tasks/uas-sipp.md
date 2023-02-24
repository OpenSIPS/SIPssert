# SIPssert Testing Framework UAS SIPP Task

This is a particularization of the [SIPp](sipp.md) task for running a UAS
[SIPp](https://sipp.sourceforge.net/) scenario.

## Behavior

Executes the `sipp` command in UAS mode.

## Defaults

The variables overwritten by default by the task are:

* `image`: the default image to run is `ctaloi/sipp`

## Settings

This task uses all the [SIPp task settings](sipp.md#settings)
Additional settings that can be passed to the task:

* `config_file`: if missing and no `sipp.xml` file in the scenario directory,
the UAS default scenario is run.

## Example

Execute a UAS scenario:
```
 - name: Waiting for call
   type: uas-sipp
   config_file: uas.xml
```

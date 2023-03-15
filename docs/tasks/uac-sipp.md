# SIPssert Testing Framework UAC SIPP Task

This is a particularization of the [SIPp](sipp.md) task for running a UAC
[SIPp](https://sipp.sourceforge.net/) scenario.

## Behavior

Executes the `sipp` command in UAC mode.

## Defaults

The variables overwritten by default by the task are:

* `image`: the default image to run is `ctaloi/sipp`

## Settings

This task uses all the [SIPp task settings](sipp.md#settings)
Additional settings that can be passed to the task:

* `proxy`: represents the outbound proxy; mandatory if `remote` is not present
* `remote`: remote destination - if present, sets the remote destination; if
`proxy` is missing, it may take `proxy`'s place
* `caller`: the identity of the caller, passed as the `caller` `key` to the
`sipp` XML scenario
* `destination`: the destination username; this is an alias to the `sipp`
`service` node
* `config_file`: if missing and no `sipp.xml` file in the scenario directory,
the UAC default scenario is run.

## Example

Execute a UAC scenario to `sip:testing@opensips.org` user:
```
 - name: Call to testing
   type: uac-sipp
   config_file: uac.xml
   destination: testing
   proxy: opensips.org
```

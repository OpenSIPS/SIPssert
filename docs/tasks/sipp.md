# SIPssert Testing Framework SIPP Task

Task that runs a [SIPp](https://sipp.sourceforge.net/) scenario.

## Behavior

The tasks execute the `sipp` command in a scenario and waits for its
termination, returning the status code of the process executed.

## Defaults

The variables overwritten by default by the task are:

* `image`: the default image to run is `ctaloi/sipp`

## Settings

Additional settings that can be passed to the task:

* `config_file`: the XML scenario file, relative to the scenario's directory,
that should be executed; if missing, the `sipp.xml` file is used if present
in the scenario's directory, otherwise one of the default scenarios are
executed, depending on the configuration of sipp
* `username`: if authentication is used in the scenario, represents the auth
username; optional, if missing and authentication is used, the scenario will
fail
* `password`: if authentication is used in the scenario, represents the auth
password; optional, if missing and authentication is used, the scenario will
fail
* `port`: the local port to bind on; optional, if missing, a random port is used
* `keys`: a dictionary representing `k: v` pairs that should be passed to the
`sipp` application as keys (check `sipp -key` parameter for more information).
* `calls`: the number of calls the scenario should handle; optional, default
`1`; if the special `unlimited` value is used, no limit is set
* `duration`: the default duration used for the `pause` nodes in the XML
scenario (see `sipp -d` parameter for more information).
* `proxy`: the SIP outbound proxy used for the scenario; if missing, the
scenario runs in UAS mode
* `service`: the destination service used to test; optional, default value is
usually `sipp` (see `sipp -s` parameter for more information).
* `scenario`: a variable that can be used in XML scenario files; it can be
added to the `keys` dictionary as well, but the default value is the name of 
the SIPssert scenario

## Example

Execute a sipp scenario defined in the `cancel.xml` file, with a domain key:

```
 - name: Cancel
   type: sipp
   config_file: cancel.xml
   keys:
     domain: opensips.org
```

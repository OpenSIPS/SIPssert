# SIPssert Testing Framework Sleep Task

The `sleep` task works like a `nop` and is used to introduce delays between
different tasks.

## Behavior

As implementation, the task runs a Debian image container running the `sleep`
command for the amount of time configured.

## Defaults

The variables overwritten by default by the task are:

* `image`: the default image to run is `debian`

## Settings

Additional settings that can be passed to the task:

* `timeout`: the amount of time to sleep, as defined in the `sleep` man page

## Example

Running a task that sleeps for 1 minute

```
 - name: One Minute
   type: sleep
   timeout: 1m
```

# SIPssert Testing Framework Generic Task

The `generic` task is the default task type, and probably the simplest one, as
it has no internal logic - it is a simple mapping to a docker container.

## Settings

* `image`: mandatory node, representing the docker image to execute
* `args`: optional arguments, passed to the image when the container is run

## Example

Running a `debian` docker container that prints the date

```
 - name: Date
   type: generic
   image: debian
   args: date
```

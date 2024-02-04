# SIPssert Testing Framework RTPProxy Task

Task used to execute [RTPProxy](https://www.rtpproxy.org/) server.

## Behavior

The task runs the `rtpproxy` media server in a `daemon` container.

## Defaults

The variables overwritten by default by the task are:

* `image`: default image to run is `sippylabs/rtpproxy:latest`
* `stop_timeout`: stopping the container is delayed with 2s

## Settings

Additional settings that can be passed to the task:

* `ip`: optional, the IP RTPProxy listens for commands from the proxy; default
* `port`: optional, the port RTPProxy listens for commands from the proxy; default
is `22222`
* `listen`: optional, the IP RTPProxy uses for sending and receiving RTP; by
default it uses all IPs available

## Example

Run a RTPProxy instance that communicates with OpenSIPS on ip 192.168.56.5 and
uses the same IP for RTP listening

```
 - name: RTPProxy Server
   type: rtpproxy
   ip: 192.168.56.5
   listen: 192.168.56.5
```

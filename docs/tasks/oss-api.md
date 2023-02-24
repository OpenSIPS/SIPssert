# SIPssert Testing Framework OSS API Task

Task used to run a [JSON-RPC](https://www.jsonrpc.org/specification) request to
a remote server.

## Behavior

The task runs a JSON-RPC command and waits for its reply - if an error node is
present in the reply, the task fails, otherwise the tasks succeeds. The command
is run using `curl` and the reply is interpreted using `jq`.

## Defaults

The variables overwritten by default by the task are:

* `image`: default image to run is `badouralix/curl-jq`

## Settings

Additional settings that can be passed to the task:

* `host`: the host to send the command to; optional, if missing, `127.0.0.1` is
used
* `port`: the port to send the command to; optional, if missing, `5000` is used
* `path`: the HTTP path to send command to; optional, if missing, defaults to
empty string
* `schema`: the HTTP schema to be used; optional, if missing, defaults to `http`
* `resource`: mandatory, the resource appended to the path, that the command is
sent to
* `command`: mandatory, represents the JSORPC method to be used
* `params`: optional parameters, expressed as dictionary, passed as params; if
missing, empty dictionary `{}` is useed

## Example

Create a user using a JSON-RPC command:

```
 - name: Create a User
   type: oss-api
   resource: user
   command: addUser
   part: jsonrpc
   host: 127.0.0.1
   port: 8080
   params:
     user: testing
```

# SIPssert Testing Framework SipExer Task

Task that runs a [SipExer](https://github.com/miconda/sipexer) User Agent.

`sipexer` is a cli tool that facilitates snding SIP requests to servers. It uses a flexible template system to allow defining many parts of the SIP request via command line parameters. It has support for UDP, TCP, TLS and WebScoket transport protocols, being suitable to test modern WebRTC SIP servers.

## Behavior

The tasks execute the `sipexer` command in a scenario and waits for its
termination, returning the status code of the process executed.

Task returns `status code: 0` when sip protocol's last response code is between 200 and 299 after call termination.
Task returns `status code: 1` when sip protocol's last response code is between 400 and 499 after call termination.
In all other cases task returns `status code: 3`

Task uses nagios plugin exit codes. See [Documentation](https://github.com/miconda/sipexer) for details.

## Defaults

The variables overwritten by default by the task are:

* `image`: the default image to run is `yaroslavonline/sipexer`

## Settings

Additional settings that can be passed to the task:

* `message`: the message section
  * `method`: SIP method used. OPTIONS, INVITE, REGISTER, INFO, NOTIFY, SUBSRIBE, PUBLISH, MESSAGE (string). Default: OPTIONS
  * `body`: message body (string) 
  * `no_body`: no body used for INVITE or MESSAGE method (true/false). Default: false
  * `content_type`: content type (string)
* `auth`: authentication credentials
  * `user`: authentication user (string)
  * `password`: authentication password (string)
  * `ha1`: authentication password in HA1 format (true/false). Default: false
* `register`: the register section
  * `expires`: expires header value (string)
  * `party`: register a third party To user (true/false). Default: false
* `from`: the From header
  * `uri`: From header URI (string)
  * `user`: From header URI username (string). Default: alice 
  * `domain`: From header URI domain (string). Default: localhost
* `to`: the To header
  * `uri`: To header URI
  * `user`: To header URI username (string). Default: bob
  * `domain`: To header URI domain (string). Default: localhost
* `ruri`: the R-URI header
  * `uri`: request uri (string)
  * `user`: request uri username for destination proxy address (string)
  * `set_domains`: set From/To domains based on R-URI (true/false). Default: false
  * `set_user`: set R-URI user to To-URI user for destination proxy address (true/false). Default: false
* `contact`: the contact section
  * `build`: build Contact header based on local address (true/false). Default: false
  * `uri`: contact uri (string)
* `extra`: extra headers. Use dict key as name, dict value as body of extra header (can be provided many times). For example,
  * `X-Custom-Header`: custom-value
  * `X-Custom-Header-2`: custom-value
* `fields`: field values. Use dict key as name, dict value as value of field (can be provided many times). List of available fields:
  * `method`. Default: "OPTIONS"
  * `fuser`. Default: "alice"
  * `fdomain`. Default: "localhost"
  * `tuser`. Default: "bob"
  * `tdomain`. Default: "localhost"
  * `viabranch`. Default: "$uuid"
  * `rport`. Default: ";rport"
  * `fromtag`. Default: "$uuid"
  * `callid`. Default: "$uuid"
  * `cseqnum`. Default: "$randseq"
  * `date`. Default: "$daterfc1123"
  * `sdpuser`. Default: "sipexer"
  * `sdpsessid`. Default: "$timestamp"
  * `sdpsessversion`. Default: "$timestamp"
  * `sdpaf`. Default: "IP4"
  * `sdprtpport`. Default: "$rand(20000,40000)"
* `template`: the template section
  * `fields_file`: path to the json fields file (string)
  * `fields_eval`: evaluate expression in fields file (true/false). Default: false
  * `file`: path to template file (string)
  * `body_file`: path for template file for body (string)
  * `raw`: send raw template content (no evaluation) (true/false). Default: false
* `user_agent`: user agent value (string)
* `logging`: the loggin section
  * `verbose`: verbosity level (0..3). Default: 2
  * `color`: color output (true/false). Default: false
* `ip`: local ip address (string)
* `port`: local port (string)
* `transport`: the transport section
  * `udp`: the UDP section
    * `dial`: attempt first connect for UDP (true/false). Default: false
  * `tls`: the TLS section
    * `key`: path to TLS private key (string)
    * `certificate`: path to TLS public certificate (string)
    * `insecure`: skip tls cerificate validation (true/false). Default: false
  * `wss`: the WebSocket section
    * `origin`: websocket origin http url (string). Default: http://127.0.0.1
    * `proto`: websocket sub-protocol (string). Default: sip
* `no_crlf`: do not replace '\n' with '\r\n' inside the data to be sent (true/false). Default: false
* `no_parse`: no SIP message parsing of input template result  
* `timeout`: the timeout section
  * `session`: time in ms to wait for a session (int)
  * `receive`: timeout in ms to wait for receive data (int). Default: 32000
  * `write`: timeout in ms to write data to socket (int). Default: 4000
* `timer`: the timer section
  * `t1`: value of t1 timer in ms (int). Default: 500
  * `t2`: value of t2 timer in ms (int). Default: 4000
* `target`: can be 'host', 'proto:host', 'host:port', 'proto:host:port', sip-uri or wss url

For more information about usage, message template, template fields, field values evaluation etc. refer [Documentation](https://github.com/miconda/sipexer)

## Example

Execute a sipexer task:

```
- name: WebRTC Call
  type: sipexer
  target: 'wss://example.com:8443/'
  message:
    method: invite
    no_body: true
  ruri:
    uri: 'sip:2002@example.com'
    set_domains: true
    set_user: true
  from:
    user: 1001
  contact:
    uri: 1001@example.com
  auth:
    user: 1001
    password: qwerty
  template:
    file: 'sipexer/template.txt'
  timeout:
    session: 2000
    write: 30000
  logging:
    verbose: 3
    color: true
```

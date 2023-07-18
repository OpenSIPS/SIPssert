# SIPssert Testing Framework Asterisk AMI Client Task

Task used to run a script using the Asterisk AMI Client

## Behavior

The task is able to communicate with one or more Asterisk instances using the
Pyst2 Python Library over the Asterisk AMI interface. 
It has two different working modes: running a batch command, or
running a script, either with the `.sh` (executed with bash), either a `.py`
file (executed with python). 

Be aware, that you should pass settings into your script on your own if you 
any script instead of default one

## Defaults

The variables overwritten by default by the task are:

* `image`: default image to run is [yaroslavonline/ami-client](https://github.com/man1207/ami-client.git)

## Settings

Additional settings that can be passed to the task:

* `script`: optional, a path to a `.sh` or `.py` script that can be executed;
if missing, [default script](https://github.com/man1207/ami-client.git) is executed
* `asterisk_ip`: required (if script is unset), the IP of the Asterisk Server
* `login`: required (if script is unset), the username to log in to the AMI
* `secret`: required (if script is unset), the secret to log in to the AMI
* `config_file`: required (if script is unset), the XML file with scenario

## Example

Listen AMI Events using Asterisk AMI Client Task

```
 - name: Control call
   type: ami-client
   script: scripts/ami-client.py
```

Listen AMI Events using Asterisk AMI Client Task using XML config

```
 - name: Control call
   type: ami-client
   asterisk_ip: 192.168.1.2
   login: developer
   secret: 12345
   config_file: scripts/ami.xml
```

## XML config structure

```xml
<eventGroups>
  <group>
      <event name="event_name" type="event_type">
        <data Header1="Value1" Header2="Value2" />
        <regex_fields>
          <field>Header2</field>
        </regex_fields>
      </event>
  </group>
</eventGroups>
```

* `eventGroups`: root node
  * `group`: groups are checked by asceding order; events inside one group are checked in any order
    * `event`: AMI event. Attributes: `name` - custom name, `type` - AMI event type (for example, PeerStatus, Newchannel etc)
      * `data`: attributes are headers and attribute values are header values. Values may be regex strings
        (for example, PeerStatus="Reachable" Peer="PJSIP/888")
      * `regex_fields`: list attributes which values should be checked as regex strings instead
        * `field`: checked field (for example, Peer)

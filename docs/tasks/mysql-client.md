# SIPssert Testing Framework MySQL Client Task

Task used to run a command line mysql client.

## Behavior

This task is able to communicate with MySQL Server instance.
It has two different working modes: running a batch command, or
running a script `.sh` (executed with bash).

## Defaults

The variables overwritten by default by the task are:

* `image`: default image to run is `opensips/mysql-client`

## Settings

Additional settings that can be passed to the task:

* `script`: optional, a path to a `.sh` script that can be executed;
if missing, the `mysql-client` tool is executed
* `host`: optional, the IP of the MySQL Server to connect; if missing,
socket `/var/run/mysqld/mysqld.sock` is used
* `port`: optional, the port of the MySQL Server to connect; if missing,
`3306` is used
* `user`: optional, the user of the MySQL Server to connect; if missing,
`root` is used
* `password`: optional, the password of the MySQL Server to connect
* `database`: optional, the database of the MySQL Server to connect
* `options`: optional, additional options of the MySQL Client; options should be formatted

## Example

Check contacts from OpenSIPS location table

scenario.yml
```yaml
- name: MySQL check Register
  type: mysql-client
  script: scripts/mysql-register.sh
  host: 192.168.52.2
```

scripts/mysql-register.sh
```bash
l=$(mysql opensips -Nse 'select count(*) from location')
if [ "$1" = "unregister" ]; then
  [ "$l" == "0"] && exit 0
else
  [ "$" == "1" ] && exit 0
fi
echo "ERROR: number of contacts is $l"
exit 1
```

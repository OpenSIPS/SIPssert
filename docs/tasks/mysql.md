# SIPssert Testing Framework MySQL Task

Task used to interact with a MySQL server, to simplify the execution and
initialization of a MySQL database.

## Usage

By default, the task starts a MySQL server with empty configuration. If you
want to initialize the database with additional files, you should put an `.sql`,
`.sh` or `.sql.gz` file containing the data in the scenario directory. This
directory will be later mounted in `/docker-entrypoint-initdb.d` and by
default, at startup, the container executes all these files in alphabetical
order, resulting in a pre-populated database.

## Defaults

The variables overwritten by default by the task are:

* `image`: default image to run is `mysql`
* `daemon`: the container run as a `daemon` task
* `mount_point`: the default mounted directory is in
`/docker-entrypoint-initdb.d`

## Settings

Additional settings that can be passed to the task:

* `root_password`: optional value, represents the root password of the mysql
server; if missing, the server will run without any password

## Example

When running a MySQL server, it is a good idea to always wait for 1s to
initialize; we do this using the `Ready` dependency:

```
 - name: MySQL Server
   type: mysql
   ready:
     Wait: 1
```

# SIPssert Testing Framework PostgreSQL Task

Task used to interact with a PostgreSQL server, to simplify the execution and
initialization of a Postgres database.

## Usage

By default, the task starts a MySQL server with empty configuration. If you
want to initialize the database with additional files, you should put an `.sql`,
`.sh` or `.sql.gz` file containing the data in the scenario directory. This
directory will be later mounted in `/docker-entrypoint-initdb.d` and by
default, at startup, the container executes all these files in alphabetical
order, resulting in a pre-populated database.

## Defaults

The variables overwritten by default by the task are:

* `image`: default image to run is `postgres`
* `daemon`: the container run as a `daemon` task
* `mount_point`: the default mounted directory is in
`/docker-entrypoint-initdb.d`

## Settings

Additional settings that can be passed to the task:

* `postgres_password`: optional value, represents the root password of the 
postgres server; default value is `postgres`

## Example

When running a Postgres server, it is a good idea to always wait for 1s to
initialize; we do this using the `Ready` dependency:

```
 - name: Postgres Server
   type: postgresql
   ready:
     Wait: 1
```

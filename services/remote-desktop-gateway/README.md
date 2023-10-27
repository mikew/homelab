# remote-desktop-gateway

[The Guacamole remote desktop gateway](https://guacamole.apache.org/).

## Installation

The Guacamole project does not have any way to seed itself. It's up to you to
download any SQL scripts and run them against your database.

Thankfully, the Postgres image for Docker has a directory you can fill with
`.sql` files and they will be executed when the database is initialized.

```shell
cd data/initdb.d/
curl -LO https://raw.githubusercontent.com/glyptodon/guacamole-client/master/extensions/guacamole-auth-jdbc/modules/guacamole-auth-jdbc-postgresql/schema/001-create-schema.sql
curl -LO https://raw.githubusercontent.com/glyptodon/guacamole-client/master/extensions/guacamole-auth-jdbc/modules/guacamole-auth-jdbc-postgresql/schema/002-create-admin-user.sql
```

## Updating

Just as Guacamole has no way to seed itself, it also has no way of migrating
its database between versions. This example is for upgrading to version 0.9.14.

```shell
# Download any migration files.
https://raw.githubusercontent.com/glyptodon/guacamole-client/master/extensions/guacamole-auth-jdbc/modules/guacamole-auth-jdbc-postgresql/schema/upgrade/upgrade-pre-0.9.14.sql

# Copy the file to the running database container.
docker cp upgrade-pre-0.9.14.sql remote-desktop-gateway-postgres-1:/upgrade-pre-0.9.14.sql

# Get into the running database container.
docker-compose exec postgres bash

# Now run psql with the migration file.
psql -f /upgrade-pre-0.9.14.sql "${POSTGRES_DATABASE}" "${POSTGRES_USER}"
```

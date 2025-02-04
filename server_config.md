# Server deployment for the BBLab-Wiki

This website is currently housed on `recall.bccfe.ca`.

The details needed to access these server can be found on the internal lab Git, 
under `dev-docs/servers.md`. If you don't already have an account on one of these
servers, ask the lab director for access.

## Table of contents
- [Dockerized deployment](#dockerized-deployment)
  * [Apache server configuration](#apache-server-configuration)
  * [Create the bind mount directories](#create-the-bind-mount-directories)
  * [Using an existing db dump in MySQL](#using-an-existing-db-dump-in-mysql)
  * [Set up the systemd services for daily log reporting](#set-up-the-systemd-services-for-daily-log-reporting)
  * [Launch containers using docker-compose](#launch-containers-using-docker-compose)
  * [SMTP authorization](#smtp-authorization)
- [Miscellaneous useful topics](#miscellaneous-useful-topics)
  * [Wiki admin](#wiki-admin)
  * [Making a db dump in MySQL](#making-a-db-dump-in-mysql)
  * [Django migrations](#django-migrations)
  * [MySQL Encoding Migration](#mysql-encoding-migration)

# Dockerized deployment

In the `dockerize-main` branch of this repo, you will find the resources needed to deploy this
server in a Docker container, currently `python:3.7-slim-buster` for backwards compatibility. 
We use an existing Traefik instance to direct HTML requests to the corresponding containers.

To deploy the server, first set up the following:

## Apache server configuration

- Note the use of the environment variable `BBLAB_WEB_ADDRESS` in [`conf/apache2.conf`].

- Alias for the `hla_class` tool, which is written in Ruby and PHP so does not work with Django:
```
Alias "/django/tools/hla_class" "/alldata/hla_class"
```
- Redirect to the main wiki page in Django. 
This line redirects with a 301 response code to `/django/wiki/` (matches only `/` or `/wiki/`):
```
RedirectMatch permanent "^\/$|^\/wiki\/$" "/django/wiki/"
```

[`conf/apache2.conf`]: conf/apache2.conf

## Create the bind mount directories

Make the following direcories on the host server:
```
/srv
 |__ bblab_site
     |
     |__ db_dump
     |   |_ db_dump.sql
     |
     |__ logs
     |
     |__ media
     |   |_ uploads (note: give group write permissions)
     |
     |__ tools
         |
         |__ guava_layout (copy existing layouts to output, preserve dates)
         |   |__ output
         |       |__ archived_layouts
         |
         |__ sequencing_layout (copy existing layouts to output, preseve dates)
             |__ output
                 |__ archived_layouts
```

Once these folders are created, perform the following permissions operations:
 - `chown -R lab:lab /srv/bblab_site` and `chmod -R g+w /srv/bblab_site`,  the webserver/docker will not be able to access directories owned by root.
 - In particular, `/srv/bblab_site/media/uploads` is used by Phlyodating to create and archive temp folders.

## Using an existing db dump in MySQL

The Django wiki is entirely stored in the database, so for dev setups, it's usually necessary to make a dump of 
the existing database on your machine to view the main site pages.

There are two Docker volumes used by the `db` container:

1. The persistent volume is stored on the host at `/srv/bblab_site/mysql`. This contains the database files used
by the MariaDB container. Without a persistent db in this location, the Django wiki will not be visible.

```
volumes:
  - /srv/bblab_site/mysql:/var/lib/mysql
```

2. An entrypoint volume containing an existing database dump at `/srv/bblab_site/db_dump`. If the db does not 
already exist in the persistent volume above, then MariaDB will load this file when the container is brought up.
Be sure to copy the `db_dump.sql` into the `/srv/bblab_site/db_dump` directory. 

```
volumes:
  - /srv/bblab_site/db_dump:/docker-entrypoint-initdb.d
```

 NOTE:
 - If you change the `db_dump.sql` file, you will need to stop the MariaDB container and delete the contents of
  `/srv/bblab_site/mysql` on your machine. Then, when starting MariaDB again, it will load the new `.sql` file.
 - The `db_dump.sql` file contains secrets. Contact the site admin if you require access to this file.

## Set up the systemd services for daily log reporting

Copy `services/phylodating.*.service` and `services/phylodating.*.timer` files to `/etc/systemd/system/`

Copy `services/bblab_site.conf` to `/usr/local/etc/`, 
 - This contains mail settings for cron jobs
 - This file contains secrets. Contact the site admin for access to this file.
 - Make sure to add `"[dev server] "` in `BBLAB_SUBJECT_PREFIX` if setting up the dev server

Copy `services/crontab_mail.py` to `/opt/`
 - This script is responsible for executing commands on the host system and sending emails if errors occur
 - The `phylodating.*.service` scripts will `docker exec` Phylodating shell scripts inside the bblab-site container
 - More log / daily scripts can be added

## Launch containers using docker-compose
Copy `.env-bblab` and `docker-compose-bblab.yml` to `/etc/docker-compose/`
 - The `.env-bblab` file contains secrets. Contact the site admin if you require access to this file.
 - Check the existing docker network which is running Traefik and set `DEFAULT_TRAEFIK_NETWORK` accordingly
 - Set the site URL (which differs for dev and prod) in the `.env-bblab` file.
 - If using standalone Traefik, uncomment the service in [`docker-compose-bblab.yml#L81-L107`]
 - Running `sudo /usr/local/bin/docker-compose --env-file ./.env-bblab -f docker-compose-bblab.yml up -d`
   will bring up the containers.

Once the container is running, you can enter a `bash` session with `docker exec -it bblab_bblab-site_1 bash -l`, 
if you need to edit these files manually.

Note that the `bblab-site` container runs the Apache server which serves the Django app, and uses the Apache configuration 
files found in `conf/`. From within the container, run `service apache2 reload` to reload the server after any manual changes.
Do NOT use `service apache2 restart`, as this will stop PID 1 and the container itself will restart.

[`docker-compose-bblab.yml#L81-L107`]: docker-compose-bblab.yml#L81-L107

## SMTP authorization

In order to send emails to addresses external to the BC-CfE, this application will authenticate with the SMTP mail server using a dedicated mail account.

The login information for this account is stored in environmental variables which are passed in to the container by `docker-compose-bblab.yml`.

Using `smptlib` the SMTP connection is put into TLS mode, using EHLO, before logging in to the server. See here: [`mailer.py#L59-L62`]:
```
smtpobj = smtplib.SMTP(os.environ['SMTP_MAIL_SERVER'], os.environ['SMTP_MAIL_PORT'])
smtpobj.starttls()
smtplib.ehlo()
smtpobj.login(os.environ['SMTP_MAIL_USER'], os.environ['SMTP_MAIL_PASSWORD'])
```

[`mailer.py#L59-L62`]: alldata/bblab_site/depend/util_scripts/mailer.py#L59-L62

# Miscellaneous useful topics

## Mounting local files for development

When doing development, it's easiest to mount your local copy of `alldata` into the container's `/alldata` directory, so that local file changes are reflected on the server immediately.

There is a second Docker compose file for this, called [`docker-compose-bblab-mounts.yml`]. To use this, start the container with the flags

```
docker-compose [--env-file <your-env-file>] -f docker-compose.bblab.yml -f docker-compose-bblab-mounts.yml up [other-flags]
```

After making file changes, it's usually necessary to run `service apache2 reload` in the container before the changes are reflected in the browser.

[`docker-compose-bblab-mounts.yml`]: docker-compose-bblab-mounts.yml

## Wiki admin

Once you have access to a staff account on the wiki, you can log in to the Django administration page at `<web-address>/django/admin` to create users and change permissions.

If you have root access to the MariaDB container, you can log in with
```
docker exec -it bblab_db_1 mysql -u root -p
```
and check the existing users with the query
```
select * from bblab_django.auth_user;
```

Note that the database table `bblab_django.auth_user_user_permissions` (and other tables that are nominally related to controlling user authorizations) may seem conspicuously empty. This is because `django-wiki` uses existing Django account statuses (superuser, staff) to determine who has access to the admin pages.

## Making a db dump in MySQL

If you need to create a new db dump for development or server migration purposes, execute the following command on the server:
```
docker exec -it <bblab-db-container-name> mysqldump -u root --password=<root-password> --all-databases > <your-db-dump-filename>.sql
```
Note that you will need login credentials for the db root user. Maybe securely bind the root password to an environment var first, otherwise the `"Enter password:"` prompt will appear in the first line of the .sql dump.

See ["Using an existing db dump in MySQL"](#using-an-existing-db-dump-in-mysql) above for more details.

## Django migrations

These should be fairly infrequent - most of the tools are model-free, so the site does not rely heavily on the database.

Django's documentation for writing a migration file is fairly straightforward, once you have a new file in one of 
the app `migrations` folders, you can run the migrations through `manage.py` as follows:

 - From within the container, navigate to `/alldata/bblab_site`
 - Run `python3 manage.py showmigrations` to see a list of migrations and their status (applied or not)
 - Apply all unapplied migrations with `python3 manage.py migrate`
 - Or, apply a specific migration with `python3 manage.py  migrate [app_label] [migration_name]`
    - For example `python3 manage.py migrate phylodating 0002`
    - If needed, you can revert by applying the previous migration, ex. `python3 manage.py migrate phylodating 0001_initial`
      will undo `0002`

## MySQL Encoding Migration

Speaking of the above `phylodating 0002`, the most recent migration was to change the column data type to allow for special characters in the `phylodating_jobs` table. Phylodating stderr has some special characters which were causing Django to fail when trying to add its model entries.

Long story short, due to column size limits, it was necessary to manually change each column to `utf8mb3`, which is MySQL's 3-byte UTF-8 encoding format. 4-byte is more of the standard UTF-8 encoding, but not so in MySQL. Three bytes encode most the UTF-8 characters that you'd encounter in Western languages & software uses, so it's probably safe enough for now.

Two useful queries to get the column encoding of a table in MySQL (from [here](https://stackoverflow.com/a/1049958)) are:

For Tables:

```
SELECT CCSA.character_set_name FROM information_schema.`TABLES` T,
       information_schema.`COLLATION_CHARACTER_SET_APPLICABILITY` CCSA
WHERE CCSA.collation_name = T.table_collation
  AND T.table_schema = "schemaname"
  AND T.table_name = "tablename";
```

For Columns:
```
SELECT character_set_name FROM information_schema.`COLUMNS` 
WHERE table_schema = "schemaname"
  AND table_name = "tablename"
  AND column_name = "columnname";
```

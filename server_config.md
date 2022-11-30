# Server deployment for the BBLab-Wiki

This website is currently migrating from its current server (housed at SFU) to
`recall-dev.bccfe.ca`, where it will reside until we are ready to host it on
`sequenceqc.bccfe.ca`.

The details needed to access these server can be found on the internal lab Git, 
under `dev-docs/servers.md`. If you don't already have an account on one of these
servers, ask the lab director for access.

## Apache deployment of original server

The current server runs on `Apache/2.4.6 (CentOS)`, there are a few customizations 
in the config file (`/etc/httpd/conf/httpd.conf`) to note:

- Alias for the `hla_class` tool, which is written in Ruby and PHP so does not work with Django:
```
Alias "/django/tools/hla_class" "/alldata/hla_class"
```
- The original Wiki page is plain HTML and incomplete, we are using the completed one in Django. 
This line redirects with a 301 response code to `/django/wiki/` (matches only `/` or `/wiki/`):
```
RedirectMatch permanent "^\/$|^\/wiki\/$" "/django/wiki/"
```

To deploy an update to this server (tracking the `main` branch of this repo), change to that directory, 
and then run `sudo git pull`. After making any changes, restart the Apache server with
`sudo systemctl restart httpd`. You can also check changes to the `httpd.conf` file 
with `sudo apachectl configtest` before restarting.

# Dockerized deployment

In the `dockerize-main` branch of this repo, you will find the resources needed to deploy this
server in a Docker container, currently `python:3.7-slim-buster` for backwards compatibility. 
We use an existing Traefik instance to direct HTML requests to the corresponding containers.

To deploy the server, first set up the following:

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

Be sure to copy the `db_dump.sql` into the `/srv/bblab_site/db_dump` directory. Without an existing db, the Django
app will crash. The two bind mounts in the MariaDB container handle db persistence:
```
volumes:
  - /srv/bblab_site/mysql:/var/lib/mysql
  - /srv/bblab_site/db_dump:/docker-entrypoint-initdb.d
```
The database files persist in the first `mysql` volume.
The second volume, mounted to `/docker-entrypoint-initdb.d` will only be loaded in the event that the db does not
already exist in the persistent directory `/var/lib/mysql`.
 - The `db_dump.sql` file contains secrets. Contact the site admin if you require access to this file.

Once these folders are created, perform the following permissions operations:
 - `chown -R lab:lab /srv/bblab_site`,  the webserver/docker will not be able to access directories owned by root
 - `chmod g+w /srv/bblab_site/media/uploads`, used by Phlyodating, which creates and archives temp folders in this directory

## Set up the systemd services for daily log reporting
Copy `service/phylodating.*.service` and `service/phylodating.*.timer` files to `/etc/systemd/system/`

Copy `service/bblab_site.conf` to `/usr/local/etc/`, 
 - This contains mail settings for cron jobs
 - This file contains secrets. Contact the site admin for access to this file.
 - Make sure to add `" [dev server]"` in `BBLAB_SUBJECT_PREFIX` if setting up the dev server

Copy `service/crontab_mail.py` to `/opt/`
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

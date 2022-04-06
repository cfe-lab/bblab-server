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

## Dockerized deployment - test server

In the `test` branch of this repo, you will find the resources needed to deploy this
server in a set of Docker containers -- one container for the Django-wiki, and a 
container housing each individual tool. We use Traefik to direct HTML requests to the
corresponding containers. The config rules for Traefik are in [`docker-compose.yml`].

Running `docker-compose up -d` in the `test` branch of this repo will build the 
`cfe-lab/bbtool-base` image, and launch the wiki/tool containers, a MariaDB container
(for Django), and Traefik. This is done by default on an external Docker network: `dock_net`. 

The `.env` file needed to set DB users and configure Django can be found on the test server,
also note that a SQL dump of the existing Django DB should be placed in `db_dump/`. This can be found
on the test server, or done manually on the original Apache server using [`django-admin dumpdata`].

Note that each wiki/tool container contains an Apache server, and uses the Apache configuration 
files found in `conf/`. 

Other files needed to build individual containers are located in `dockerfiles/` and `urls/`.
Scripts and Django views for individual tools are found in the `alldata/bblab_site/tools/` directory.

Special steps are required for the `hla_class` and `phylodating` tools, as these require access
to parent directories in the `alldata/` folder.

[`docker-compose.yml`]: docker-compose.yml
[`django-admin dumpdata`]: https://docs.djangoproject.com/en/2.2/ref/django-admin/#dumpdata

## Migrating from the original Apache server to the Dockerized server

The containerized test server is intended to replace the original server, by migrating individual tools
to a new CfE server while directing HTML requests for the remainder of the site back to the original
server.

``` mermaid
flowchart LR
    id1(GET bblab-hivresearch.ca/django/tools/some-tool<br/>GET bblab-hivresearch.ca/django/tools/another-tool<br/>etc)-->Traefik
    Traefik---->another-tool
    Traefik---->yet-another-tool
    subgraph New Server
    Traefik
    Traefik-->some-tool
    end
    subgraph Old Server
    another-tool
    yet-another-tool
    end
```

An example of partial deployment (used on the `recall-dev.bccfe.ca` server) is here: 
[`docker-compose-ttc.yml`]. This gives an example of migrating the `text-to-columns` tool to a new server.

[`docker-compose-ttc.yml`]: docker-compose-ttc.yml

In order to direct bblab-server containers to connect to Traefik on the existing Docker network,
we set the environmental variable

```
DEFAULT_TRAEFIK_NETWORK=dock_default
```

this is used in `docker-compose-ttc.yml` as follows:

```
networks:
  bb-external:
    external: true
    name: ${DEFAULT_TRAEFIK_NETWORK?error default network undefined}
  bb-internal:
    external: false

services:
  text-to-columns:
    [...]
    networks:
      - bb-external
      - bb-internal
    expose: [80]
    [...]
    labels:
      - "traefik.docker.network=${DEFAULT_TRAEFIK_NETWORK?error default network undefined}"
```

The Traefik configuration needed to move the DNS from the old to the new server is still under investigation.
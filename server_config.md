# Configuring the Apache server for the BBLab-Wiki

The details needed to access this server can be found on the internal lab Git, 
under `dev-docs/servers.md`. If you don't already have an account on the server, 
ask the lab director for access.

The server runs on `Apache/2.4.6 (CentOS)`, there are a few customizations 
in the config file (`/etc/httpd/conf/httpd.conf`) to note:

- Alias for the `hla_class` tool, which is written in Ruby and PHP so does not work with Django.
The link [`https://bblab-hivresearchtools.ca/django/tools/hla_class/`] maps to `/alldata/hla_class`:
```
Alias "/django/tools/hla_class" "/alldata/hla_class"
```
- Redirect the main URL [`https://bblab-hivresearchtools.ca/`] to [`https://bblab-hivresearchtools.ca/django/wiki/`]. 
The original Wiki page is plain HTML and incomplete, we are using the completed one in Django. 
This line redirects with a 301 response code to `/django/wiki/` matches only `/` or `/wiki/`:
```
RedirectMatch permanent "^\/$|^\/wiki\/$" "/django/wiki/"
```

The source code for each project will be deployed with a Git clone at
`/alldata/bblab_site/tools/<name_of_tool>`. Most are not up-to-date with Git.
To deploy an update, change to that directory, and then run `sudo git pull`.

After making any changes, restart the Apache server with
`sudo systemctl restart httpd`. You can also check changes to the `httpd.conf` file 
with `sudo apachectl configtest` before restarting.
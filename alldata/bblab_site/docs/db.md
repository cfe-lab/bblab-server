# 2020-12-21
I was getting an error:

```
2020-12-21 11:50:40,649 log 29996 139761871329024 Internal Server Error: /django/wiki/
Traceback (most recent call last):
  File "/usr/local/lib/python3.7/site-packages/django/db/backends/base/base.py", line 216, in ensure_connection
    self.connect()
  File "/usr/local/lib/python3.7/site-packages/django/db/backends/base/base.py", line 194, in connect
    self.connection = self.get_new_connection(conn_params)
  File "/usr/local/lib/python3.7/site-packages/django/db/backends/mysql/base.py", line 227, in get_new_connection
    return Database.connect(**conn_params)
  File "/usr/local/lib/python3.7/site-packages/MySQLdb/__init__.py", line 84, in Connect
    return Connection(*args, **kwargs)
  File "/usr/local/lib/python3.7/site-packages/MySQLdb/connections.py", line 166, in __init__
    super(Connection, self).__init__(*args, **kwargs2)
MySQLdb._exceptions.OperationalError: (2002, "Can't connect to local MySQL server through socket '/var/lib/mysql/mysql.sock' (2)")
```

To fix it:

```bash
systemctl start mariadb.service
systemctl enable mariadb.service
```

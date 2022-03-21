#!/bin/bash
find /alldata/bblab_site/media/uploads -maxdepth 1 -mindepth 1 -type d -mtime +7 -exec rm -r {} \;

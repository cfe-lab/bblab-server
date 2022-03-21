FROM cfe-lab/bbtool-base:latest

COPY conf/tools-gld.conf /etc/apache2/mods-available
RUN ln -sf /etc/apache2/mods-available/tools-gld.conf /etc/apache2/mods-enabled/tools-gld.conf

COPY alldata/bblab_site/static/gld* /alldata/bblab_site/static/
COPY urls/urls_guava_layout.py /alldata/bblab_site/tools/urls.py

COPY alldata/bblab_site/tools/guava_layout /alldata/bblab_site/tools/guava_layout
RUN groupadd varwwwusers
RUN usermod -a -G varwwwusers www-data
RUN chgrp -R varwwwusers /alldata/bblab_site/tools/guava_layout/output

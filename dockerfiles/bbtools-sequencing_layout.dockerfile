FROM cfe-lab/bbtool-base:latest

COPY conf/tools-pld.conf /etc/apache2/mods-available
RUN ln -sf /etc/apache2/mods-available/tools-pld.conf /etc/apache2/mods-enabled/tools-pld.conf

COPY alldata/bblab_site/static/pld* /alldata/bblab_site/static/
COPY urls/urls_sequencing_layout.py /alldata/bblab_site/tools/urls.py

COPY alldata/bblab_site/tools/sequencing_layout /alldata/bblab_site/tools/sequencing_layout
RUN groupadd varwwwusers
RUN usermod -a -G varwwwusers www-data
RUN chgrp -R varwwwusers /alldata/bblab_site/tools/sequencing_layout/output

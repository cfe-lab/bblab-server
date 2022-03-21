FROM cfe-lab/bbtool-base:latest

COPY alldata/bblab_site/static/tcr_d* /alldata/bblab_site/static/
COPY urls/urls_tcr_distance.py /alldata/bblab_site/tools/urls.py

COPY alldata/bblab_site/tools/tcr_distance /alldata/bblab_site/tools/tcr_distance
RUN groupadd varwwwusers
RUN usermod -a -G varwwwusers www-data
RUN chgrp -R varwwwusers /alldata/bblab_site/tools/tcr_distance/tmp_dirs

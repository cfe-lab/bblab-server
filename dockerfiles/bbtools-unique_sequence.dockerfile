FROM cfe-lab/bbtool-base:latest

COPY alldata/bblab_site/tools/unique_sequence /alldata/bblab_site/tools/unique_sequence
COPY alldata/bblab_site/static/usc* /alldata/bblab_site/static/
COPY urls/urls_unique_sequence.py /alldata/bblab_site/tools/urls.py
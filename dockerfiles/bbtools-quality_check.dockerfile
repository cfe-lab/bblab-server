FROM cfe-lab/bbtool-base:latest

COPY alldata/bblab_site/tools/quality_check /alldata/bblab_site/tools/quality_check
COPY alldata/bblab_site/static/qc* /alldata/bblab_site/static/
COPY urls/urls_quality_check.py /alldata/bblab_site/tools/urls.py
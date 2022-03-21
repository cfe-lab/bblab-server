FROM cfe-lab/bbtool-base:latest

RUN apt-get update && apt-get install -qq r-base r-base-dev

COPY alldata/bblab_site/tools/qvalue /alldata/bblab_site/tools/qvalue
COPY alldata/bblab_site/static/qv* /alldata/bblab_site/static/
COPY urls/urls_qvalue.py /alldata/bblab_site/tools/urls.py
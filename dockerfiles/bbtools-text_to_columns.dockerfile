FROM cfe-lab/bbtool-base:latest

COPY alldata/bblab_site/tools/text_to_columns /alldata/bblab_site/tools/text_to_columns
COPY alldata/bblab_site/static/ttc_css/ /alldata/bblab_site/static/ttc_css/
COPY alldata/bblab_site/static/ttc* /alldata/bblab_site/static/
COPY urls/urls_text_to_columns.py /alldata/bblab_site/tools/urls.py
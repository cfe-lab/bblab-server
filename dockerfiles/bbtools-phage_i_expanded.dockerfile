FROM cfe-lab/bbtool-base:latest

COPY alldata/bblab_site/tools/phage_i_expanded /alldata/bblab_site/tools/phage_i_expanded
COPY alldata/bblab_site/static/PIex_css/ /alldata/bblab_site/static/PIex_css/
COPY alldata/bblab_site/static/PI* /alldata/bblab_site/static/
COPY urls/urls_phage_i_expanded.py /alldata/bblab_site/tools/urls.py
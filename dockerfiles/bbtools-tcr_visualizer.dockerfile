FROM cfe-lab/bbtool-base:latest

COPY alldata/bblab_site/tools/tcr_visualizer /alldata/bblab_site/tools/tcr_visualizer
COPY alldata/bblab_site/static/tcr_v* /alldata/bblab_site/static/
COPY urls/urls_tcr_visualizer.py /alldata/bblab_site/tools/urls.py
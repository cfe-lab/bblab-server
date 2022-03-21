FROM cfe-lab/bbtool-base:latest

COPY alldata/bblab_site/tools/variable_function /alldata/bblab_site/tools/variable_function
COPY alldata/bblab_site/static/vfa_css/ /alldata/bblab_site/static/vfa_css/ 
COPY urls/urls_variable_function.py /alldata/bblab_site/tools/urls.py
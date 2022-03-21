FROM cfe-lab/bbtool-base:latest

COPY alldata/bblab_site/tools/best_prob_HLA_imputation /alldata/bblab_site/tools/best_prob_HLA_imputation
COPY alldata/bblab_site/static/bphi_css/ /alldata/bblab_site/static/bphi_css/
COPY alldata/bblab_site/static/bphi* /alldata/bblab_site/static/
COPY urls/urls_bphi.py /alldata/bblab_site/tools/urls.py
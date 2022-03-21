FROM cfe-lab/bbtool-base:latest

COPY alldata/bblab_site/tools/translate_DNA /alldata/bblab_site/tools/translate_DNA
COPY alldata/bblab_site/static/dna_css/ /alldata/bblab_site/static/dna_css/
COPY alldata/bblab_site/static/dna* /alldata/bblab_site/static/
COPY urls/urls_translate_dna.py /alldata/bblab_site/tools/urls.py
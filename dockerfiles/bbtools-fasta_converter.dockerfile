FROM cfe-lab/bbtool-base:latest

COPY alldata/bblab_site/tools/fasta_converter /alldata/bblab_site/tools/fasta_converter
COPY alldata/bblab_site/static/fas_css/ /alldata/bblab_site/static/fas_css/
COPY alldata/bblab_site/static/fa* /alldata/bblab_site/static/
COPY urls/urls_fasta_converter.py /alldata/bblab_site/tools/urls.py
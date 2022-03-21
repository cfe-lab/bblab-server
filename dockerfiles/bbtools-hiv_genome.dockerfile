FROM cfe-lab/bbtool-base:latest

COPY alldata/bblab_site/tools/HIV_genome /alldata/bblab_site/tools/HIV_genome
COPY alldata/bblab_site/static/genome_css/ /alldata/bblab_site/static/genome_css/
COPY urls/urls_hiv_genome.py /alldata/bblab_site/tools/urls.py
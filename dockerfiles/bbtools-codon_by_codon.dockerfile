FROM cfe-lab/bbtool-base:latest

RUN apt-get update && apt-get install -qq r-base r-base-dev

COPY alldata/bblab_site/tools/codon_by_codon /alldata/bblab_site/tools/codon_by_codon
COPY alldata/bblab_site/static/cbc* /alldata/bblab_site/static/
COPY urls/urls_codon_by_codon.py /alldata/bblab_site/tools/urls.py
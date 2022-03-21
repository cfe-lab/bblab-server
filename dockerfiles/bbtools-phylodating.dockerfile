FROM cfe-lab/bbtool-base:latest

# ENV R_BASE_VERSION 3.5.2

RUN apt-get update \
	&& apt-get install -qq libxml2-dev libcurl4-openssl-dev libssl-dev \
	&& apt-get install -qq \
			r-base \
			r-base-dev \
			littler r-cran-littler \
	&& ln -s /usr/lib/R/site-library/littler/examples/install.r /usr/local/bin/install.r \
	&& ln -s /usr/lib/R/site-library/littler/examples/install2.r /usr/local/bin/install2.r \
	&& ln -s /usr/lib/R/site-library/littler/examples/installBioc.r /usr/local/bin/installBioc.r \
	&& ln -s /usr/lib/R/site-library/littler/examples/installDeps.r /usr/local/bin/installDeps.r \
	&& ln -s /usr/lib/R/site-library/littler/examples/installGithub.r /usr/local/bin/installGithub.r \
	&& ln -s /usr/lib/R/site-library/littler/examples/testInstalled.r /usr/local/bin/testInstalled.r \
	&& install.r docopt \
	&& rm -rf /tmp/downloaded_packages/ /tmp/*.rds \
	&& rm -rf /var/lib/apt/lists/*

RUN install2.r --error \
	ape \
	optparse \
	ggplot2 \
	# ggtree \
	dplyr \
	chemCal \
	magrittr \
	tidytree \
	lubridate \
	data.table \
	BiocManager

RUN R -e "install.packages(\"https://cran.r-project.org/src/contrib/Archive/rvcheck/rvcheck_0.1.8.tar.gz\", repos = NULL)" \
 && R -e "BiocManager::install(\"ggtree\", force=TRUE)"

COPY alldata/bblab_site/tools/phylodating /alldata/bblab_site/tools/phylodating
COPY urls/urls_phylodating.py /alldata/bblab_site/tools/urls.py
COPY phylodating_setup/settings_phylodating.py /alldata/bblab_site/bblab_site/settings.py

COPY alldata/bblab_site/manage.py /alldata/bblab_site/
COPY alldata/bblab_site/__init__.py /alldata/bblab_site/
COPY alldata/bblab_site/media /alldata/bblab_site/media
RUN groupadd varwwwusers
RUN usermod -a -G varwwwusers www-data
RUN chgrp -R varwwwusers /alldata/bblab_site/media

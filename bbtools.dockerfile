FROM python:3.7-slim-buster AS bblab-server

LABEL maintainer=jkai@bccfe.ca

ARG DEBIAN_FRONTEND=noninteractive

ENV PYTHONUNBUFFERED 1


RUN apt-get update -qq --fix-missing && \
  apt-get install -qq --no-install-recommends apt-utils && \
  apt-get install -qq unzip wget vim curl && \
  apt-get install -qq python3-dev python \
    default-libmysqlclient-dev \
    build-essential \
    apache2 apache2-dev \
    libapache2-mod-wsgi-py3 \
    php libapache2-mod-php \
    ruby-full && \
  curl https://bootstrap.pypa.io/pip/2.7/get-pip.py --output get-pip.py && \
  python2 get-pip.py


# Install R with Bioconductor and libs for Phylodating
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
	dplyr \
	chemCal \
	magrittr \
	tidytree \
	lubridate \
	data.table \
	BiocManager
RUN R -e "install.packages(\"https://cran.r-project.org/src/contrib/Archive/rvcheck/rvcheck_0.1.8.tar.gz\", repos = NULL)" \
 && R -e "BiocManager::install(\"ggtree\", force=TRUE)"

RUN rm -rf /var/lib/apt/lists/*


# set the timezone for Vancouver, so that datetime.now() returns our
# local time, not UTC.
RUN apt-get -y install tzdata
ENV TZ=America/Vancouver
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone


# we define these users here so that we can launch an image as a local user
# see the Makefile in the top directory...
RUN useradd -rm -s /bin/tcsh -u 1000 dockuser00 &&\
    useradd -rm -s /bin/tcsh -u 1001 dockuser01 &&\
    useradd -rm -s /bin/tcsh -u 1002 dockuser02 &&\
    useradd -rm -s /bin/tcsh -u 1003 dockuser03 &&\
    useradd -rm -s /bin/tcsh -u 1004 dockuser04

# copy source code
COPY alldata /alldata


# Install Ruby dependencies
# bundler v1.17.2 is needed for older libraries
COPY hla_class_setup/Gemfile ./
RUN gem install bundler:1.17.2
RUN bundle install

# Install Python dependencies:
COPY alldata/bblab_site/requirements.txt .
COPY alldata/bblab_site/requirements27.txt .
RUN pip3 install --no-cache-dir -r requirements.txt
RUN pip2 install --no-cache-dir -r requirements27.txt


# load configuration for Apache server
COPY conf/apache2.conf /etc/apache2/
COPY conf/tools-*.conf /etc/apache2/mods-available/
COPY conf/php.conf /etc/apache2/mods-available
RUN ln -sf /etc/apache2/mods-available/tools-gld.conf /etc/apache2/mods-enabled/tools-gld.conf && \
    ln -sf /etc/apache2/mods-available/tools-pld.conf /etc/apache2/mods-enabled/tools-pld.conf && \
    ln -sf /etc/apache2/mods-available/tools-hla.conf /etc/apache2/mods-enabled/tools-hla.conf && \
    ln -sf /etc/apache2/mods-available/php.conf /etc/apache2/mods-enabled/php.conf && \
    ln -sf /var/log/apache2/access.log /dev/stdout && \
    ln -sf /var/log/apache2/error.log /dev/stderr && \
    chmod 766 -R /var/log/apache2/ && \
    a2dissite 000-default.conf && a2dissite default-ssl.conf


# Set permissions and ownership for WSGI user/group (www-data:varwwwusers)
RUN groupadd varwwwusers && \
    usermod -a -G varwwwusers www-data && \
    mkdir /alldata/bblab_site/tools/sequencing_layout/output && \
    mkdir /alldata/hla_class/tmp && \
    mkdir /alldata/bblab_site/media && \
    mkdir /alldata/bblab_site/logs && \
    chmod 766 -R /alldata/bblab_site/tools/guava_layout/output && \
    chown -R www-data:varwwwusers /alldata/bblab_site/tools/guava_layout/output && \
    chmod 766 -R /alldata/bblab_site/tools/sequencing_layout/output && \
    chown -R www-data:varwwwusers /alldata/bblab_site/tools/sequencing_layout/output && \
    chmod 766 -R /alldata/bblab_site/tools/tcr_distance/tmp_dirs && \
    chown -R www-data:varwwwusers /alldata/bblab_site/tools/tcr_distance/tmp_dirs && \
    chmod 766 -R /alldata/hla_class/tmp && \
    chown -R www-data:varwwwusers /alldata/hla_class/tmp && \
    chmod 766 -R /alldata/bblab_site/media && \
    chown -R www-data:varwwwusers /alldata/bblab_site/media && \
    chmod 766 -R /alldata/bblab_site/static && \
    chown -R www-data:varwwwusers /alldata/bblab_site/static && \
    chmod 766 /alldata/bblab_site/logs && \
    chown www-data:varwwwusers /alldata/bblab_site/logs


# ---finish up

# CI fields, ARG is set at build time, then made available as an ENV for the container to use
# LABELs are also appended to the image for housekeeping purposes.
ARG CI_BUILD_DATE='n/a'
ARG CI_BUILD_USER='n/a'
ARG CI_BUILD_COMMENTS='n/a'

ENV BUILD_DATE=$CI_BUILD_DATE \
    BUILD_USER=$CI_BUILD_USER \
    BUILD_COMMENTS=$CI_BUILD_COMMENTS

LABEL build_date=$CI_BUILD_DATE \
      build_user=$CI_BUILD_USER

# change default directory when entering container with --build-arg (ex: `--build-arg WORKINGDIR=projects/qual_nimbusprecision`)
#ignoring this will set it to the standard directory
ARG WORKINGDIR=alldata
WORKDIR /$WORKINGDIR
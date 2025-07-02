FROM ubuntu:24.04 AS bblab-site

LABEL maintainer=vmysak@bccfe.ca

ARG DEBIAN_FRONTEND=noninteractive

ENV PYTHONUNBUFFERED 1

SHELL ["bash", "-l", "-c"]

# Refresh package repositories.
RUN apt-get update -qq -y

# Install some apt related programs.
RUN apt-get install -qq --no-install-recommends apt-utils software-properties-common dirmngr

# Install system packages.
RUN apt-get install -qq unzip wget vim curl \
        python3-dev python3-pip \
        default-libmysqlclient-dev \
        build-essential tzdata \
        apache2 apache2-dev \
        libapache2-mod-wsgi-py3 \
        php libapache2-mod-php \
        libxml2-dev libcurl4-openssl-dev libssl-dev \
        gfortran liblapack-dev libblas-dev libopenblas-dev git

# set the timezone for Vancouver, so that datetime.now() returns our
# local time, not UTC.
ENV TZ=America/Vancouver
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Install R with Bioconductor and libs for Phylodating
RUN wget -qO- https://cloud.r-project.org/bin/linux/ubuntu/marutter_pubkey.asc | tee -a /etc/apt/trusted.gpg.d/cran_ubuntu_key.asc && \
    add-apt-repository "deb https://cloud.r-project.org/bin/linux/ubuntu $(lsb_release -cs)-cran40/" && \
    apt-get update -qq

ENV R_BASE_VERSION 4.4.2

RUN apt-get install -q -y --no-install-recommends \
                    r-base=${R_BASE_VERSION}-* \
                    r-base-dev=${R_BASE_VERSION}-* \
                    r-base-core=${R_BASE_VERSION}-* \
                    littler r-cran-littler

RUN true \
	&& ln -s /usr/lib/R/site-library/littler/examples/install.r /usr/local/bin/install.r \
	&& ln -s /usr/lib/R/site-library/littler/examples/install2.r /usr/local/bin/install2.r \
	&& ln -s /usr/lib/R/site-library/littler/examples/installBioc.r /usr/local/bin/installBioc.r \
	&& ln -s /usr/lib/R/site-library/littler/examples/installDeps.r /usr/local/bin/installDeps.r \
	&& ln -s /usr/lib/R/site-library/littler/examples/installGithub.r /usr/local/bin/installGithub.r \
	&& ln -s /usr/lib/R/site-library/littler/examples/testInstalled.r /usr/local/bin/testInstalled.r \
	&& install.r docopt

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
RUN rm -rf /tmp/downloaded_packages/ /tmp/*.rds \
    rm -rf /var/lib/apt/lists/*

# Install Ruby dependencies
# bundler v1.17.2 is needed for older libraries
RUN curl -fsSL https://github.com/rbenv/rbenv-installer/raw/HEAD/bin/rbenv-installer | bash
RUN /root/.rbenv/bin/rbenv init - --no-rehash bash > /root/.bashrc
RUN rbenv install 2.5.5
RUN rbenv global 2.5.5
COPY hla_class_setup/Gemfile ./
RUN gem install bundler:1.17.2
RUN bundle install

# Install Python dependencies:
COPY alldata/bblab_site/requirements.txt .
RUN pip3 install --break-system-packages --no-cache-dir -r requirements.txt

# # Set user/group for Apache/Django execution
RUN groupadd varwwwusers && \
    usermod -a -G varwwwusers www-data

WORKDIR /tmp/download

RUN wget https://github.com/cfe-lab/bblab-server/releases/download/v0.1.0-alpha/blast-2.2.16-x64-linux.tar.gz && \
    wget https://github.com/cfe-lab/bblab-server/releases/download/v0.1.0-alpha/tcrdist_extras_v2.tgz && \
    tar -xzf blast-2.2.16-x64-linux.tar.gz && \
    tar -xzf tcrdist_extras_v2.tgz

# copy source code
COPY alldata /alldata

RUN chown -R www-data:varwwwusers /alldata /tmp/download

USER www-data

# Run setup for tcr-dist
RUN mv ./tcrdist_extras_v2/external/ /alldata/bblab_site/depend/apps/tcr-dist/ && \
    mv ./blast-2.2.16/ /alldata/bblab_site/depend/apps/tcr-dist/external/ && \
    mv ./tcrdist_extras_v2/datasets/ /alldata/bblab_site/depend/apps/tcr-dist/ && \
    mv ./tcrdist_extras_v2/db/ /alldata/bblab_site/depend/apps/tcr-dist/ && \
    mv ./tcrdist_extras_v2/testing_ref/ /alldata/bblab_site/depend/apps/tcr-dist/ && \
    chmod -R 766 /alldata/bblab_site/depend/apps/tcr-dist/external && \
    chown -R www-data:varwwwusers /alldata/bblab_site/depend/apps/tcr-dist/external && \
    chmod -R 766 /alldata/bblab_site/depend/apps/tcr-dist/datasets && \
    chown -R www-data:varwwwusers /alldata/bblab_site/depend/apps/tcr-dist/datasets && \
    chmod -R 766 /alldata/bblab_site/depend/apps/tcr-dist/db && \
    chown -R www-data:varwwwusers /alldata/bblab_site/depend/apps/tcr-dist/db && \
    chmod -R 766 /alldata/bblab_site/depend/apps/tcr-dist/testing_ref && \
    chown -R www-data:varwwwusers /alldata/bblab_site/depend/apps/tcr-dist/testing_ref && \
    rm blast-2.2.16-x64-linux.tar.gz && \
    rm tcrdist_extras_v2.tgz && \
    rm -r tcrdist_extras_v2

USER root

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

# Copy shell scripts for Phylodating
COPY phylodating_setup/clean.sh /var/www/phylodating/clean.sh
COPY phylodating_setup/logwatcher.sh /var/www/phylodating/logwatcher.sh

# Set permissions and ownership for WSGI user/group (www-data:varwwwusers)
RUN mkdir -p /alldata/bblab_site/tools/sequencing_layout/output && \
    mkdir /alldata/bblab_site/tools/sequencing_layout/output/archived_layouts && \
    mkdir /alldata/bblab_site/tools/sequencing_layout/output/archived_layouts/old_archived_layouts && \
    mkdir /alldata/bblab_site/tools/guava_layout/output/archived_layouts && \
    mkdir /alldata/bblab_site/tools/guava_layout/output/archived_layouts/old_archived_layouts && \
    mkdir /alldata/hla_class/tmp && \
    mkdir -p /alldata/bblab_site/media && \
    mkdir -p /alldata/bblab_site/logs && \
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
    chmod 777 /alldata/bblab_site/logs && \
    chown -R www-data:varwwwusers /alldata/bblab_site/logs

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
ARG WORKINGDIR=/alldata
WORKDIR $WORKINGDIR

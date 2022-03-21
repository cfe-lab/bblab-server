FROM ruby:2.6-slim-buster

LABEL maintainer=jkai@bccfe.ca

ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get update -qq --fix-missing && \
    apt-get install -y --no-install-recommends apt-utils

RUN apt-get install -qq unzip wget vim

RUN apt-get install -qq build-essential \
  apache2 apache2-dev \
  php libapache2-mod-php

# throw errors if Gemfile has been modified since Gemfile.lock
# RUN bundle install
# RUN bundle config --global frozen 1
COPY hla_class_setup/Gemfile ./
RUN bundle install

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
COPY alldata/bblab_site/account /alldata/bblab_site/account
COPY alldata/bblab_site/bblab_site /alldata/bblab_site/bblab_site
COPY alldata/bblab_site/depend /alldata/bblab_site/depend
COPY alldata/bblab_site/templates /alldata/bblab_site/templates
# COPY alldata /alldata

# seem to need the update here...
RUN apt-get update

# RUN apt-get install -qq gpg gnupg2 curl && \
#     curl -sSL https://rvm.io/mpapis.asc | gpg --import - && \
#     curl -sSL https://rvm.io/pkuczynski.asc | gpg --import - && \
#     echo 409B6B1796C275462A1703113804BB82D39DC0E3:6: | gpg2 --import-ownertrust # mpapis@gmail.com && \
#     echo 7D2BAF1CF37B13E2069D6956105BD0E739499BDB:6: | gpg2 --import-ownertrust # piotr.kuczynski@gmail.com && \
#     curl -sSL https://get.rvm.io | bash -s stable && \
#     source /etc/profile.d/rvm.sh | rvm install 2.6.0 && | rvm use 2.6.0 --default

RUN rm -rf /var/lib/apt/lists/*

# change default directory when entering container with --build-arg (ex: `--build-arg WORKINGDIR=projects/qual_nimbusprecision`)
#ignoring this will set it to the standard directory
ARG WORKINGDIR=alldata
WORKDIR /$WORKINGDIR

COPY alldata/hla_class /alldata/hla_class
# RUN chmod ugo+rwx /alldata/hla_class/tmp
RUN groupadd varwwwusers
RUN usermod -a -G varwwwusers www-data
RUN chgrp -R varwwwusers /alldata/hla_class/tmp

# load configuration for Apache server
# COPY 001-bblab.conf /etc/apache2/sites-available/
COPY conf/tools-hla.conf /etc/apache2/mods-available
COPY conf/php.conf /etc/apache2/mods-available
RUN ln -sf /etc/apache2/mods-available/tools-hla.conf /etc/apache2/mods-enabled/tools-hla.conf && \
    ln -sf /etc/apache2/mods-available/php.conf /etc/apache2/mods-enabled/php.conf
COPY conf/apache2-hla_class.conf /etc/apache2/apache2.conf
RUN a2dissite 000-default.conf && a2dissite default-ssl.conf
RUN ln -sf /var/log/apache2/access.log /dev/stdout && \
    ln -sf /var/log/apache2/error.log /dev/stderr 
RUN chmod 766 -R /var/log/apache2/

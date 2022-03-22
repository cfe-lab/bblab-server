FROM python:3.7-slim-buster AS bblab-base

LABEL maintainer=jkai@bccfe.ca

ARG DEBIAN_FRONTEND=noninteractive

ENV PYTHONUNBUFFERED 1

RUN apt-get update -qq --fix-missing && \
  apt-get install -y --no-install-recommends apt-utils

RUN apt-get install -qq unzip wget vim

# RUN apt-key adv --keyserver pgp.mit.edu --recv-keys 3A79BD29 && \
#     dpkg -i mysql-apt-config_0.8.22-1_all.deb

RUN apt-get install -qq python3-dev \
  default-libmysqlclient-dev \
  build-essential \
  apache2 apache2-dev \
  libapache2-mod-wsgi-py3

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
# RUN apt-get update
 
RUN rm -rf /var/lib/apt/lists/*

# set Python virtual environment
# RUN python -m pip install virtualenv
# ENV VIRTUAL_ENV=/opt/venv
# RUN python3 -m venv $VIRTUAL_ENV
# ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Install dependencies:
COPY alldata/bblab_site/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# change default directory when entering container with --build-arg (ex: `--build-arg WORKINGDIR=projects/qual_nimbusprecision`)
#ignoring this will set it to the standard directory
ARG WORKINGDIR=alldata
WORKDIR /$WORKINGDIR


FROM bblab-base AS bblab-wiki

# copy source code
COPY alldata /alldata
COPY urls/urls_empty.py /alldata/bblab_site/tools/urls.py

# load configuration for Apache server
COPY conf/apache2.conf /etc/apache2/
# COPY django_wsgi_conf.py /etc/django/
RUN ln -sf /var/log/apache2/access.log /dev/stdout && \
    ln -sf /var/log/apache2/error.log /dev/stderr 
RUN chmod 766 -R /var/log/apache2/
RUN a2dissite 000-default.conf && a2dissite default-ssl.conf

# ---finish up
# webserver uses port 8000
# EXPOSE 8000

# we expect to override this when deploying live, but if we leave the user as root then it causes issues with tests.
# USER 1000:1000

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



FROM bblab-base AS bblab-tool

# copy source code
# COPY alldata/bblab_site/tools/urls_all.py /alldata/bblab_site/tools/
COPY alldata/bblab_site/static/tool_style.css /alldata/bblab_site/static/
COPY alldata/bblab_site/static/wo_style.css /alldata/bblab_site/static/
COPY alldata/bblab_site/static/account_style.css /alldata/bblab_site/static/
COPY alldata/bblab_site/static/auth_style.css /alldata/bblab_site/static/

# load configuration for Apache server
COPY conf/apache2.conf /etc/apache2/
# COPY django_wsgi_conf.py /etc/django/
RUN ln -sf /var/log/apache2/access.log /dev/stdout && \
    ln -sf /var/log/apache2/error.log /dev/stderr 
RUN a2dissite 000-default.conf && a2dissite default-ssl.conf
RUN chmod 766 -R /var/log/apache2/

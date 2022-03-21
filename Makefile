# makefile for building and running 
# the bblab test server docker images
#
# We have the following docker images (for now just one)
# 1: bbtools-base

BASE_IMAGE_NAME = bbtools-base
BASE_DOCKERFILE = ${BASE_IMAGE_NAME}.dock
BASE_CONTAINER_NAME = bbtools-base-container

TOP_DIR = ${CURDIR}

ALLDATA_DIR   =${TOP_DIR}/alldata

# pytest outputs are written to /tmp in the docker instance --
# mount these here so we can inspect test output from outside the container
DOCKERTEMPDIR=${TOP_DIR}/docktemp

# these mounts are for code development --
DEV_DIR_MOUNTS = -v ${ALLDATA_DIR}

PROD_DIR_MOUNTS =
# -v ${OUTREPORTDIR}:/monthlyreports

ALL_DIR_MOUNTS = ${DEV_DIR_MOUNTS} ${PROD_DIR_MOUNTS}

# the hostname that the webserver should be reachable under for
# development. This works in conjunction with a reverse proxy image
# if /etc/hosts has an appropriate entry
WEBSERVER_HOSTNAME = bbtools-test.bccfe.ca

BUILD_USER = ${USERNAME}
BUILD_TIME = $(shell date --iso=seconds)

BUILD_ARGS = --build-arg CI_BUILD_DATE=${BUILD_TIME} --build-arg CI_BUILD_USER=${BUILD_USER}

# the preferred workdir on launching a container...
RUN_PWD = /projects



default: help

# NOTE: this code taken from https://gist.github.com/rcmachado/af3db315e31383502660
help: ## This Makefile can be used to build and run the alignment docker images.
	$(info Available targets:)
	@awk '/^[a-zA-Z\-\_0-9]+:/ {                                   \
          nb = sub( /^## /, "", helpMsg );                             \
          if(nb == 0) {                                                \
            helpMsg = $$0;                                             \
            nb = sub( /^[^:]*:.* ## /, "", helpMsg );                  \
          }                                                            \
          if (nb)                                                      \
            printf "\033[1;31m%-" width "s\033[0m %s\n", $$1, helpMsg; \
        }                                                              \
        { helpMsg = $$0 }'                                             \
        width=$$(grep -o '^[a-zA-Z_0-9]\+:' $(MAKEFILE_LIST) | wc -L)  \
	$(MAKEFILE_LIST)

build-base: ${BASE_DOCKERFILE} ## build the alignment-base docker image
	docker build -f ${BASE_DOCKERFILE} -t ${BASE_IMAGE_NAME} ${BUILD_ARGS} .
build-base-nocache: ## build the alignment-base docker image from scratch
	docker build --no-cache -f ${BASE_DOCKERFILE} -t ${BASE_IMAGE_NAME} ${BUILD_ARGS} .
#--
run-base-prod: ## run the alignment-base docker image as the current non-root user (production mounts)
	docker run --rm --name ${BASE_CONTAINER_NAME} --net=host -e VIRTUAL_HOST=${WEBSERVER_HOSTNAME} --user $$(id -u):$$(id -g) -it ${PROD_DIR_MOUNTS} ${BASE_IMAGE_NAME}
run-base-local: ## run the alignment-base docker image as the current non-root user with mounting local code directories
	docker run --rm --name ${BASE_CONTAINER_NAME} --net=host -e VIRTUAL_HOST=${WEBSERVER_HOSTNAME} --user $$(id -u):$$(id -g) -it ${ALL_DIR_MOUNTS} ${BASE_IMAGE_NAME}
run-base-root: ## run the alignment-base docker image as the current non-root user with mounting local code directories
	docker run --rm --name ${BASE_CONTAINER_NAME} -it -p9000:9000 ${ALL_DIR_MOUNTS} ${BASE_IMAGE_NAME}
clean: ## clean up the local directory
	rm -rf *~ .pytest_cache

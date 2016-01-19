FROM radioastro/base:0.2
MAINTAINER gijsmolenaar@gmail.com

RUN apt-get update && \
    apt-get -y install meqtrees casarest && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*


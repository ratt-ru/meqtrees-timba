FROM kernsuite/base:3

RUN docker-apt-install libblitz0-dev python-dev casacore-dev libblas-dev liblapack-dev libqdbm-dev wcslib-dev \
 libfftw3-dev python-numpy libcfitsio3-dev casarest libboost-thread-dev libboost-system-dev cmake g++
ADD . /code
RUN mkdir /code/build
WORKDIR /code/build
RUN cmake ..
RUN make -j4

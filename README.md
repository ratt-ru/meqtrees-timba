# MeqTrees Timba

MeqTrees is a software package for implementing Measurement Equations. This makes it uniquely suited for simulation and calibration of radioastronomical data, especially that involving new radiotelescopes and observational regimes.

# Installation

## Obtaining the source

The meqtrees-timba source code is maintained on github. You can obtain it using:

```
$ git clone https://github.com/ska-sa/meqtrees-timba
```

## Requirements

To compile meqtrees-timba you need to meet the following requirements:

* cmake
* blitz++
* python
* casacore (3.0 or greater)
* casarest (1.3.1 or greater)
* blas
* lapack
* libgdm
* wcslib
* fftw3
* cfitsio


## Compilation

In the casacore source folder run:
```
mkdir build
cd build
cmake ..
make
make install
```


## Ubuntu packages

If you run Ubuntu we recommand the KERN packages:

http://kernsuite.info


# Documentation

Read everything about MeqTrees on the wiki:

https://github.com/ska-sa/meqtrees/wiki


# Travis

[![Build Status](https://travis-ci.org/ska-sa/meqtrees-timba.png)](https://travis-ci.org/ska-sa/meqtrees-timba)

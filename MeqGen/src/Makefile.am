SUBDIRS	= .

lib_LTLIBRARIES 	= libmeqgen.la

DOCHDRS = \
  meqFlagger.h \
  meqCopy.h \
  meqCompare.h \
  meqDFT_GVD.h \
  meqShiftPhaseCentre.h 

libmeqgen_la_SOURCES 	= $(DOCHDRS)  \
meqFlagger.cc \
meqCopy.cc \
meqCompare.cc \
meqDFT_GVD.cc \
meqShiftPhaseCentre.cc \
AID-MeqGen-Registry.cc

include $(lofar_sharedir)/Makefile.common
include $(lofar_sharedir)/Makefile.aids

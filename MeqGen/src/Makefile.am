# Jan -- edit this list to add node classes
AUTOGEN_NODES = meqCopy.cc

# do not edit below this point

SUBDIRS	= .

lib_LTLIBRARIES 	= libmeqgen.la

libmeqgen_la_SOURCES 	= $(AUTOGEN_NODES) \
	AID-MeqGen-Registry.cc

AIDHDRS = $(addsuffix .h,$(basename $(AUTOGEN_NODES)))

include $(lofar_sharedir)/Makefile.common
include $(lofar_sharedir)/Makefile.aids

AM_CPPFLAGS = -DMAKE_LOFAR_SYMBOLS_GLOBAL

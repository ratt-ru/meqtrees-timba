dmi_dir = $(lofar_sharedir)/../DMI

CXXFLAGS += -D_GNU_SOURCE 

check_PROGRAMS		= test_mstoms test_octo_mstoms

bin_PROGRAMS   		= 

test_mstoms_SOURCES		    = test_mstoms.cc
test_mstoms_LDADD		      = ../src/libapputils.la
test_mstoms_DEPENDENCIES	= ../src/libapputils.la $(LOFAR_DEPEND)

test_octo_mstoms_SOURCES		    = test_octo_mstoms.cc
test_octo_mstoms_LDADD		      = ../src/libapputils.la
test_octo_mstoms_DEPENDENCIES	= ../src/libapputils.la $(LOFAR_DEPEND)

TESTS				=  

EXTRA_DIST			=

# script used to generate AID maps
MAPBUILDER = $(dmi_dir)/src/build_aid_maps.pl 

# All .aidlist files below this dir will be scanned
BASELISTDIR = $(lofar_sharedir)/..

# Your package's subdirectory
AID_DIR = $(top_srcdir)/test

aids:
	$(MAPBUILDER) `find $(BASELISTDIR) -name \*.aidlist` $(AID_DIR)/*.h

include $(lofar_sharedir)/Makefile.common

AM_CPPFLAGS = -DMAKE_LOFAR_SYMBOLS_GLOBAL

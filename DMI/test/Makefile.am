CXXFLAGS += -Wno-unknown-pragmas

INCLUDES			= -I$(top_srcdir)/src \
                -I$(lofar_sharedir)/../CEP/CPA/PSCF/src \
                -I$(lofar_sharedir)/../src-links

check_PROGRAMS			= test_dmi tDataArray

test_dmi_SOURCES 		= test_dmi.cc
test_dmi_LDADD			= $(top_builddir)/src/libdmi.la

tDataArray_SOURCES 		= tDataArray.cc
tDataArray_LDADD		= $(top_builddir)/src/libdmi.la

TESTS				= test_dmi tDataArray

EXTRA_DIST			=

# script used to generate AID maps
MAPBUILDER = $(top_srcdir)/src/build_aid_maps.pl 

# All .aidlist files below this dir will be scanned
BASELISTDIR = $(lofar_sharedir)/..

# Your package's subdirectory
AID_DIR = $(top_srcdir)/test

aids:
	$(MAPBUILDER) `find $(BASELISTDIR) -name \*.aidlist` $(AID_DIR)/*.h


include $(lofar_sharedir)/Makefile.common

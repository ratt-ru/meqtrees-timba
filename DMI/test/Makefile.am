CXXFLAGS += -Wno-unknown-pragmas

INCLUDES			= -I$(lofar_sharedir)/../CEP/CPA/PSCF/src

check_PROGRAMS			= test_dmi tDataArray

test_dmi_SOURCES 		= test_dmi.cc
test_dmi_LDADD			= $(top_builddir)/src/libdmi.la \
      $(lofar_sharedir)/../Common/build/gnu_debug/src/libcommon.la

tDataArray_SOURCES 		= tDataArray.cc
tDataArray_LDADD		= $(top_builddir)/src/libdmi.la \
      $(lofar_sharedir)/../Common/build/gnu_debug/src/libcommon.la

TESTS	=					\
	test_dmi				
#	tDataArray_test.sh			

#EXTRA_DIST = 					\
#	tDataArray_test.sh			
#	tDataArray.out				


# script used to generate AID maps
MAPBUILDER = $(top_srcdir)/src/build_aid_maps.pl 

# All .aidlist files below this dir will be scanned
BASELISTDIR = $(lofar_sharedir)/..

# Your package's subdirectory
AID_DIR = $(top_srcdir)/test

aids:
	$(MAPBUILDER) `find $(BASELISTDIR) -name \*.aidlist` $(AID_DIR)/*.h


include $(lofar_sharedir)/Makefile.common

CXXFLAGS += -D_GNU_SOURCE 
# CXXFLAGS += -D_GNU_SOURCE -DUSE_THREADS -pthread

check_PROGRAMS		= test_dmi test_thread tDataArray ncperf test_reg
bin_PROGRAMS      = 

test_dmi_SOURCES 	= test_dmi.cc
test_dmi_LDADD		= ../src/libdmi.la 
test_dmi_DEPENDENCIES	= ../src/libdmi.la $(LOFAR_DEPEND)

test_reg_SOURCES 	= test_reg.cc
test_reg_LDADD		= ../src/libdmi.la 
test_reg_DEPENDENCIES	= ../src/libdmi.la $(LOFAR_DEPEND)

ncperf_SOURCES 	= ncperf.cc
ncperf_LDADD		= ../src/libdmi.la 
ncperf_DEPENDENCIES	= ../src/libdmi.la $(LOFAR_DEPEND)

test_thread_SOURCES = test_thread.cc
test_thread_LDADD		= ../src/libdmi.la 
test_thread_DEPENDENCIES	= ../src/libdmi.la $(LOFAR_DEPEND)

tDataArray_SOURCES 	= tDataArray.cc
tDataArray_LDADD	= ../src/libdmi.la 
tDataArray_DEPENDENCIES	= ../src/libdmi.la $(LOFAR_DEPEND)

TESTS	=					\
	test_dmi				\
	tDataArray_test.sh			

EXTRA_DIST = 					\
	tDataArray_test.sh			\
	tDataArray.out				

# script used to generate AID maps
MAPBUILDER = $(top_srcdir)/src/build_aid_maps.pl 

# All .aidlist files below this dir will be scanned
BASELISTDIR = $(lofar_sharedir)/..

# Your package's subdirectory
AID_DIR = $(top_srcdir)/test

aids:
	$(MAPBUILDER) `find $(BASELISTDIR) -name \*.aidlist` $(AID_DIR)/*.h


include $(lofar_sharedir)/Makefile.common

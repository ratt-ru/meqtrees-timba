dmi_dir = $(lofar_sharedir)/../DMI



CXXFLAGS += -D_GNU_SOURCE 

check_PROGRAMS		= 

bin_PROGRAMS   		= IMTest glish_reflector

# test_glish_SOURCES 	= test_glish.cc EchoWP.cc AID-Testing-Registry.cc
#
# test_glish_LDADD		= ../src/Glish/liboctopussy-glish.la \
#  ../src/liboctopussy.la -lglish -lsos -lnpd
#
# test_glish_DEPENDENCIES	= ../src/liboctopussy.la $(LOFAR_DEPEND)

IMTest_SOURCES		= IMTestWP.h IMTestWP.cc IMTest.cc 
IMTest_LDADD		  = ../src/liboctoglish.la -lglish -lsos -lnpd
IMTest_DEPENDENCIES	= ../src/liboctoglish.la $(LOFAR_DEPEND)

glish_reflector_SOURCES		    = glish_reflector.cc
glish_reflector_LDADD		      = ../src/liboctoglish.la -lglish -lsos -lnpd
glish_reflector_DEPENDENCIES	= ../src/liboctoglish.la $(LOFAR_DEPEND)

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

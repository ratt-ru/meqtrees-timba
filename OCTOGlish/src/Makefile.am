dmi_dir = $(lofar_sharedir)/../DMI


CXXFLAGS += -Wall -Wno-unknown-pragmas -Wno-deprecated -D_GNU_SOURCE

lib_LTLIBRARIES = liboctoglish.la

liboctoglish_la_SOURCES = GlishClientWP.cc AID-OCTOGlish-Registry.cc

bin_PROGRAMS   		= octoglish

octoglish_SOURCES 	= octoglish.cc 

octoglish_LDADD		= liboctoglish.la -lglish -lsos -lnpd
  
#  ../../test/AID-Testing-Registry.o 

octoglish_DEPENDENCIES	= liboctoglish.la $(LOFAR_DEPEND)

#  ../../test/AID-Testing-Registry.o 
  
include $(lofar_sharedir)/Makefile.common



# script used to generate AID maps
MAPBUILDER = $(dmi_dir)/src/build_aid_maps.pl 

# All .aidlist files below this dir will be scanned
BASELISTDIR = $(lofar_sharedir)/..

# Your package's subdirectory
AID_DIR = $(top_srcdir)/src

aids:
	$(MAPBUILDER) `find $(BASELISTDIR) -name \*.aidlist` $(AID_DIR)/*.h 
 

include $(lofar_sharedir)/Makefile.common

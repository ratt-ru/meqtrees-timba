CXXFLAGS += -Wno-unknown-pragmas -pg -DDMI_THREADS

INCLUDES = -I$(top_srcdir)/src

dmi_dir = $(lofar_sharedir)/../DMI

check_PROGRAMS		= test_octopussy

bin_PROGRAMS   		= test_gw test_gw0 test_ping test_glish

test_octopussy_SOURCES 	= test_octopussy.cc EchoWP.cc AID-Testing-Registry.cc

test_octopussy_LDADD		= $(top_builddir)/src/liboctopussy.la -lpthread

test_octopussy_DEPENDENCIES	= $(top_builddir)/src/liboctopussy.la $(LOFAR_DEPEND)

test_gw_SOURCES 	= test_gw.cc EchoWP.cc AID-Testing-Registry.cc

test_gw_LDADD		= $(top_builddir)/src/liboctopussy.la -lpthread 

test_gw_DEPENDENCIES	= $(top_builddir)/src/liboctopussy.la $(LOFAR_DEPEND)

test_gw0_SOURCES 	= test_gw0.cc AID-Testing-Registry.cc

test_gw0_LDADD		= $(top_builddir)/src/liboctopussy.la -lpthread 

test_gw0_DEPENDENCIES	= $(top_builddir)/src/liboctopussy.la $(LOFAR_DEPEND)

test_ping_SOURCES 	= test_ping.cc EchoWP.cc AID-Testing-Registry.cc

test_ping_LDADD		= $(top_builddir)/src/liboctopussy.la -lpthread 

test_ping_DEPENDENCIES	= $(top_builddir)/src/liboctopussy.la $(LOFAR_DEPEND)

test_glish_SOURCES 	= test_glish.cc EchoWP.cc AID-Testing-Registry.cc

test_glish_LDADD		= $(top_builddir)/src/Glish/liboctopussy-glish.la \
  $(top_builddir)/src/liboctopussy.la -lglish -lsos -lnpd -lpthread

test_glish_DEPENDENCIES	= $(top_builddir)/src/liboctopussy.la $(LOFAR_DEPEND)

TESTS				=  test_octopussy

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

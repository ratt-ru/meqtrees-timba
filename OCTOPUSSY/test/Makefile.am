CXXFLAGS += -D_GNU_SOURCE 

DOCHDRS = EchoWP.h

dmi_dir = $(lofar_sharedir)/../DMI

check_PROGRAMS		= test_octopussy test_gw test_gw0 test_ping

bin_PROGRAMS   		= 

test_octopussy_SOURCES 	= test_octopussy.cc EchoWP.cc AID-Testing-Registry.cc

test_octopussy_LDADD		= ../src/liboctopussy.la -lpthread

test_octopussy_DEPENDENCIES	= ../src/liboctopussy.la $(LOFAR_DEPEND)

test_gw_SOURCES 	= test_gw.cc EchoWP.cc AID-Testing-Registry.cc

test_gw_LDADD		= ../src/liboctopussy.la -lpthread 

test_gw_DEPENDENCIES	= ../src/liboctopussy.la $(LOFAR_DEPEND)

test_gw0_SOURCES 	= test_gw0.cc AID-Testing-Registry.cc

test_gw0_LDADD		= ../src/liboctopussy.la -lpthread 

test_gw0_DEPENDENCIES	= ../src/liboctopussy.la $(LOFAR_DEPEND)

test_ping_SOURCES 	= test_ping.cc EchoWP.cc AID-Testing-Registry.cc

test_ping_LDADD		= ../src/liboctopussy.la -lpthread 

test_ping_DEPENDENCIES	= ../src/liboctopussy.la $(LOFAR_DEPEND)

TESTS				=  test_octopussy

EXTRA_DIST			=

include $(lofar_sharedir)/Makefile.common
include $(lofar_sharedir)/Makefile.aids

AM_CPPFLAGS = -DMAKE_LOFAR_SYMBOLS_GLOBAL

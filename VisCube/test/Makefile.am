CXXFLAGS += -D_GNU_SOURCE -Wno-unused

check_PROGRAMS		= test_viscube

bin_PROGRAMS   		= 

test_viscube_SOURCES 	= test_viscube.cc 

test_viscube_LDADD		= $(top_builddir)/src/libviscube.la 

test_viscube_DEPENDENCIES	= $(top_builddir)/src/libviscube.la $(LOFAR_DEPEND)

TESTS				=  test_viscube

EXTRA_DIST			=

include $(lofar_sharedir)/Makefile.common

AM_CPPFLAGS = -DMAKE_LOFAR_SYMBOLS_GLOBAL

CXXFLAGS += -Wall -Wno-unknown-pragmas -Wno-deprecated -D_GNU_SOURCE -I/usr/include/python2.3

lib_LTLIBRARIES = octopython_c.la

DOCHDRS = OctoPython.h

octopython_c_la_SOURCES = \
  octopython.cc ProxyWPObject.cc DataConv.cc
  
octopython_c_la_LDFLAGS = -module

octopython_c_la_LIBADD = -llog4cplus

octopython_c_la_DEPENDENCIES = \
  ../pkgbldinc/OCTOPUSSY/liboctopussy.la \
  ../pkgbldinc/DMI/libdmi.la \
  ../pkgbldinc/Common/libcommon.la

check_PROGRAMS   		= 

include $(lofar_sharedir)/Makefile.aids
include $(lofar_sharedir)/Makefile.common

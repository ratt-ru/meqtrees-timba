CXXFLAGS += -Wall -Wno-unknown-pragmas -Wno-deprecated -D_GNU_SOURCE -I/usr/include/python2.3

lib_LTLIBRARIES = py_app_launcher.la

DOCHDRS = OctoPython.h

py_app_launcher_la_SOURCES = \
  py_app_launcher.cc
  
py_app_launcher_la_LDFLAGS = -module

py_app_launcher_la_LIBADD = $(lofar_sharedir)/../CEP/CPA/AppAgent/AppAgent/build/gnu3_debug/src/libappagent.la \
  -llog4cplus 

py_app_launcher_la_DEPENDENCIES = \
  ../pkgbldinc/OCTOPUSSY/liboctopussy.la \
  ../pkgbldinc/DMI/libdmi.la \
  ../pkgbldinc/Common/libcommon.la

check_PROGRAMS   		= 

include $(lofar_sharedir)/Makefile.aids
include $(lofar_sharedir)/Makefile.common

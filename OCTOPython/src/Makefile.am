CXXFLAGS += -Wall -Wno-unknown-pragmas -Wno-deprecated -D_GNU_SOURCE -I/usr/include/python2.3

lib_LTLIBRARIES = octopython.la

DOCHDRS = OctoPython.h

octopython_la_SOURCES = \
  octopython.cc ProxyWPObject.cc ThreadCond.cc DataConv.cc
  
octopython_la_LDFLAGS = -module

octopython_la_LIBADD = -llog4cplus

octopython_la_DEPENDENCIES = \
  ../pkgbldinc/OCTOPUSSY/liboctopussy.la \
  ../pkgbldinc/DMI/libdmi.la \
  ../pkgbldinc/Common/libcommon.la

check_PROGRAMS   		= 

pythondir = $(libexecdir)/python
dist_python_SCRIPTS = \
  dmitypes.py dmi_repr.py \
  octopussy.py qt_threading.py

include $(lofar_sharedir)/Makefile.aids
include $(lofar_sharedir)/Makefile.common

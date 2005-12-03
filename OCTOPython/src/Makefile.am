CXXFLAGS += -Wall -Wno-unknown-pragmas -Wno-deprecated -D_GNU_SOURCE -I/usr/include/python2.3

lib_LTLIBRARIES = octopython.la liboctopython.la

DOCHDRS = OctoPython.h

octopython_la_SOURCES = \
  octopython.cc ProxyWPObject.cc ThreadCond.cc DataConv.cc
  
octopython_la_LDFLAGS = -module

liboctopython.la:
	@ln -s octopython.la liboctopython.la

# octopython_la_LIBADD = 

octopython_la_DEPENDENCIES = \
  ../pkgbldinc/OCTOPUSSY/liboctopussy.la \
  ../pkgbldinc/DMI/libdmi.la \
  ../pkgbldinc/Common/libcommon.la

check_PROGRAMS   		= 

pythondir = $(libexecdir)/python

timbadir = $(pythondir)/Timba

dist_timba_SCRIPTS = __init__.py \
  dmi.py dmi_repr.py utils.py \
  octopussy.py qt_threading.py

include $(lofar_sharedir)/Makefile.aids
include $(top_srcdir)/Makefile.common

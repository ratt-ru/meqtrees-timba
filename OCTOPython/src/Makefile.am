CXXFLAGS += -Wall -Wno-unknown-pragmas -Wno-deprecated -D_GNU_SOURCE

# lib_LTLIBRARIES = octopython.la liboctopython.la

lib_LTLIBRARIES = octopython.la liboctopython.la

DOCHDRS = OctoPython.h

octopython_la_SOURCES = \
  octopython.cc ProxyWPObject.cc LazyObjRef.cc ThreadCond.cc DataConv.cc

octopython_la_LDFLAGS = -module

octopython_la_LIBADD =  \
  ../pkgbldinc/TimBase/.libs/libtimbase.a \
  ../pkgbldinc/DMI/.libs/libdmi.a

octopython_la_DEPENDENCIES = \
  ../pkgbldinc/TimBase/.libs/libtimbase.a \
  ../pkgbldinc/DMI/.libs/libdmi.a
  

liboctopython_la_SOURCES = \
  octopython.cc ProxyWPObject.cc LazyObjRef.cc ThreadCond.cc DataConv.cc

liboctopython_la_LDFLAGS = 



check_PROGRAMS   		= 

pythondir = $(libexecdir)/python

timbadir = $(pythondir)/Timba

dist_timba_SCRIPTS = __init__.py \
  dmi.py dmi_repr.py utils.py \
  octopussy.py qt_threading.py

include $(lofar_sharedir)/Makefile.aids
include $(top_srcdir)/Makefile.common

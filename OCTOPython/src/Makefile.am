CXXFLAGS += -Wall -Wno-unknown-pragmas -Wno-deprecated -D_GNU_SOURCE

# lib_LTLIBRARIES = octopython.la liboctopython.la

lib_LTLIBRARIES = liboctopython.la

DOCHDRS = OctoPython.h

liboctopython_la_SOURCES = \
  octopython.cc ProxyWPObject.cc LazyObjRef.cc ThreadCond.cc DataConv.cc

liboctopython_la_LDFLAGS = 

all: $(srcdir)/version_info/svn_revision.py

$(srcdir)/version_info/svn_revision.py:	FORCE
	(cd $(top_srcdir); vv="`svnversion`"; echo "svn_revision='$$vv'" ) >$@
	
FORCE:

check_PROGRAMS   		= 

pythondir = $(libexecdir)/python

timbadir = $(pythondir)/Timba

dist_timba_SCRIPTS = __init__.py \
  dmi.py dmi_repr.py utils.py \
  octopussy.py qt_threading.py

include $(lofar_sharedir)/Makefile.aids
include $(top_srcdir)/Makefile.common

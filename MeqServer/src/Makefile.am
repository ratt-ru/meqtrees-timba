CXXFLAGS += -Wno-unknown-pragmas -Wno-deprecated -D_GNU_SOURCE -I/usr/include/python2.3

dmi_dir = $(lofar_sharedir)/../DMI

LDFLAGS += -L/usr/lib -Wl,-v

## these ought to be brought in via configure
# LIBS += -llapack -lblas -lg2c -lfftw3

lib_LTLIBRARIES = libmeqserver.la

DOCHDRS = MeqServer.h MeqPython.h VisDataMux.h VisHandlerNode.h Sink.h Spigot.h

libmeqserver_la_SOURCES = \
  AID-MeqServer-Registry.cc \
  MeqServer.cc MeqPython.cc \
  VisDataMux.cc \
  VisHandlerNode.cc \
  Sink.cc Spigot.cc
  
bin_PROGRAMS   		= meqserver
  
meqserver_SOURCES		    = meqserver.cc
meqserver_LDADD		      = libmeqserver.la -lpython2.3 
# NB: older systems may require -ldl -lutil as well
meqserver_DEPENDENCIES	= libmeqserver.la $(LOFAR_DEPEND)

check_PROGRAMS = octolistener

octolistener_SOURCES 	= octolistener.cc
octolistener_LDADD		= libmeqserver.la
octolistener_DEPENDENCIES	= libmeqserver.la $(LOFAR_DEPEND)


include $(top_srcdir)/Makefile.common
include $(lofar_sharedir)/Makefile.aids


AM_CPPFLAGS = -DMAKE_LOFAR_SYMBOLS_GLOBAL

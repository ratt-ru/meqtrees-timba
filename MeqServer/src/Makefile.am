CXXFLAGS += -Wno-unknown-pragmas -Wno-deprecated -D_GNU_SOURCE

dmi_dir = $(lofar_sharedir)/../DMI

lib_LTLIBRARIES = libmeqserver.la

DOCHDRS = \
  MeqServer.h MeqPython.h \
  VisDataMux.h VisHandlerNode.h Sink.h Spigot.h \
  MeqUtils.h \
  PyNode.h PyTensorFuncNode.h

libmeqserver_la_SOURCES = \
  AID-MeqServer-Registry.cc \
  MeqServer.cc MeqPython.cc mequtils.cc \
  VisDataMux.cc \
  VisHandlerNode.cc \
  Sink.cc Spigot.cc \
  PyNode.cc PyTensorFuncNode.cc
  

bin_PROGRAMS   		= meqserver
  
meqserver_SOURCES	      = meqserver_main.cc
meqserver_LDADD		      = libmeqserver.la 
# NB: older systems may require -ldl -lutil as well
meqserver_DEPENDENCIES	= libmeqserver.la $(LOFAR_DEPEND)



check_PROGRAMS = octolistener

octolistener_SOURCES 	= octolistener.cc
octolistener_LDADD		= libmeqserver.la
octolistener_DEPENDENCIES	= libmeqserver.la $(LOFAR_DEPEND)


include $(top_srcdir)/Makefile.common
include $(lofar_sharedir)/Makefile.aids


AM_CPPFLAGS = -DMAKE_LOFAR_SYMBOLS_GLOBAL

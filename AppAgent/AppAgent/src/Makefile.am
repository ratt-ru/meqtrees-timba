lib_LTLIBRARIES = libappagent.la

DOCHDRS = \
  AppEventAgentBase.h  BOIOSink.h      \
  AppAgent.h         AppEventFlag.h       FileSink.h \
  AppControlAgent.h  AppEventSink.h       

libappagent_la_SOURCES = \
  AID-AppAgent-Registry.cc \
  AppAgent.cc \
  AppEventSink.cc \
  AppEventAgentBase.cc \
  AppEventFlag.cc \
  AppControlAgent.cc \
  FileSink.cc \
  BOIOSink.cc 
  

include $(lofar_sharedir)/Makefile.common
include $(lofar_sharedir)/Makefile.aids


AM_CPPFLAGS = -DMAKE_LOFAR_SYMBOLS_GLOBAL

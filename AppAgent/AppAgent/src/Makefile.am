lib_LTLIBRARIES = libappagent.la

DOCHDRS = \
  AppEventAgentBase.h BOIOSink.h                        \
  AppAgent.h          AppEventFlag.h    FileSink.h      \
  AppControlAgent.h   AppEventSink.h                    \
  OctoEventSink.h     OctoEventMultiplexer.h            \
  DataStreamMap.h     InputAgent.h                      \
  OutputAgent.h       VisAgentVocabulary.h
  
libappagent_la_SOURCES = \
  AID-AppAgent-Registry.cc \
  AppAgent.cc \
  AppEventSink.cc \
  AppEventAgentBase.cc \
  AppEventFlag.cc \
  AppControlAgent.cc \
  FileSink.cc \
  BOIOSink.cc \
  OctoEventSink.cc \
  OctoEventMultiplexer.cc \
  DataStreamMap.cc InputAgent.cc OutputAgent.cc

include $(top_srcdir)/Makefile.common
include $(lofar_sharedir)/Makefile.aids

AM_CPPFLAGS = -DMAKE_LOFAR_SYMBOLS_GLOBAL

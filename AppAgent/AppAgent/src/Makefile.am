lib_LTLIBRARIES = libappagent.la

DOCHDRS = \
  EventFlag.h     OctoChannel.h  BOIOChannel.h    \
  EventChannel.h  FileChannel.h  OctoEventMux.h   \
  MTQueueChannel.h \
  VisDataVocabulary.h
 
libappagent_la_SOURCES = \
  AID-AppAgent-Registry.cc            \
  BOIOChannel.cc  EventChannel.cc     \
  EventFlag.cc    FileChannel.cc      \
  OctoChannel.cc  OctoEventMux.cc     \
  MTQueueChannel.cc 

include $(top_srcdir)/Makefile.common
include $(lofar_sharedir)/Makefile.aids

AM_CPPFLAGS = -DMAKE_LOFAR_SYMBOLS_GLOBAL

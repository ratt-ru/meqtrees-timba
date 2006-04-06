lib_LTLIBRARIES = libapputils.la

DOCHDRS = MSInputChannel.h MSOutputChannel.h MSChannelVocabulary.h 

libapputils_la_SOURCES = AID-AppUtils-Registry.cc \
  MSInputChannel.cc MSOutputChannel.cc MSSeqOutputChannel.cc \
  MSChannelDebugContext.cc 

glishdir = $(libexecdir)/glish/appagent
dist_glish_SCRIPTS = app_proxy.g app_defaults.g

include $(top_srcdir)/Makefile.common
include $(lofar_sharedir)/Makefile.aids

AM_CPPFLAGS = -DMAKE_LOFAR_SYMBOLS_GLOBAL

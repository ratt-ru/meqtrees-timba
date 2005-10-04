lib_LTLIBRARIES = libapputils.la

DOCHDRS = VisPipe.h ApplicationBase.h VisRepeater.h \
          MSInputSink.h MSOutputSink.h MSVisAgentVocabulary.h

libapputils_la_SOURCES = AID-AppUtils-Registry.cc \
  ApplicationBase.cc VisPipe.cc VisRepeater.cc \
  MSInputSink.cc MSOutputSink.cc \
  MSVisAgentDebugContext.cc 

glishdir = $(libexecdir)/glish/appagent
dist_glish_SCRIPTS = app_proxy.g app_defaults.g

include $(top_srcdir)/Makefile.common
include $(lofar_sharedir)/Makefile.aids

AM_CPPFLAGS = -DMAKE_LOFAR_SYMBOLS_GLOBAL

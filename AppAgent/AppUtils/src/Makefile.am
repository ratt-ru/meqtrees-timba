DOCHDRS = VisPipe.h ApplicationBase.h VisRepeater.h

lib_LTLIBRARIES = libapputils.la

libapputils_la_SOURCES = \
  ApplicationBase.cc VisPipe.cc VisRepeater.cc AID-AppUtils-Registry.cc

glishdir = $(libexecdir)/glish/appagent
dist_glish_SCRIPTS = app_proxy.g app_defaults.g

include $(lofar_sharedir)/Makefile.common
include $(lofar_sharedir)/Makefile.aids


AM_CPPFLAGS = -DMAKE_LOFAR_SYMBOLS_GLOBAL

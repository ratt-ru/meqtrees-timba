lib_LTLIBRARIES = libapputils.la

DOCHDRS = MSInputChannel.h MSOutputChannel.h MSChannelVocabulary.h 

libapputils_la_SOURCES = AID-AppUtils-Registry.cc \
  MSInputChannel.cc MSOutputChannel.cc MSSeqOutputChannel.cc \
  MSChannelDebugContext.cc 
  
  
bin_PROGRAMS   		= addbitflagcol
  
addbitflagcol_SOURCES	      = addbitflagcol.cc
addbitflagcol_LDADD	      = 
# NB: older systems may require -ldl -lutil as well
addbitflagcol_DEPENDENCIES	= $(LOFAR_DEPEND)



glishdir = $(libexecdir)/glish/appagent
dist_glish_SCRIPTS = app_proxy.g app_defaults.g

include $(top_srcdir)/Makefile.common
include $(lofar_sharedir)/Makefile.aids

AM_CPPFLAGS = -DMAKE_LOFAR_SYMBOLS_GLOBAL

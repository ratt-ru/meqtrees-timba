CXXFLAGS += -Wall -Wno-unknown-pragmas -Wno-deprecated -D_GNU_SOURCE

lib_LTLIBRARIES = liboctoglish.la

DOCHDRS = GlishClientWP.h GlishThreadWP.h GlishConnServerWP.h GlishUtil.h

liboctoglish_la_SOURCES = \
  GlishClientWP.cc GlishThreadWP.cc GlishConnServerWP.cc \
  GlishUtil.cc AID-OCTOGlish-Registry.cc

check_PROGRAMS   		= octoglishserver

#octoglish_SOURCES 	= octoglish.cc 

#octoglish_LDADD		= liboctoglish.la 
  
#octoglish_DEPENDENCIES	= liboctoglish.la $(LOFAR_DEPEND)

octoglishserver_SOURCES 	= octoglishserver.cc 

octoglishserver_LDADD		= liboctoglish.la 
  
octoglishserver_DEPENDENCIES	= liboctoglish.la $(LOFAR_DEPEND)

glishdir = $(libexecdir)/glish
dist_glish_SCRIPTS = octopussy.g
  
include $(lofar_sharedir)/Makefile.aids
include $(lofar_sharedir)/Makefile.common

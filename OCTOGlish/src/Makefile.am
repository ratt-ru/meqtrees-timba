CXXFLAGS += -Wall -Wno-unknown-pragmas -Wno-deprecated -D_GNU_SOURCE

lib_LTLIBRARIES = liboctoglish.la

DOCHDRS = GlishClientWP.h GlishUtil.h

liboctoglish_la_SOURCES = GlishClientWP.cc GlishUtil.cc AID-OCTOGlish-Registry.cc

check_PROGRAMS   		= octoglish

octoglish_SOURCES 	= octoglish.cc 

octoglish_LDADD		= liboctoglish.la 
  
octoglish_DEPENDENCIES	= liboctoglish.la $(LOFAR_DEPEND)

glishdir = $(libexecdir)/glish
dist_glish_SCRIPTS = octopussy.g
  
include $(lofar_sharedir)/Makefile.aids
include $(lofar_sharedir)/Makefile.common
